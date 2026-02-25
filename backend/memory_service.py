"""
Graphiti 记忆层服务 — FIFO Queue 版本

架构：
  写入：WriteRequest → asyncio.Queue（FIFO）→ 单一 worker 顺序调用 graphiti
  读取：Search = graphiti 已处理 facts  +  队列中尚未处理的 pending 原文

  这样无论 graphiti 处理快慢，搜索都能拿到完整的记忆视图。

Run: uvicorn memory_service:app --port 8000 --reload
"""

import asyncio
import hashlib
import logging
import os
import re
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'external', 'graphiti'))

from graphiti_core import Graphiti  # noqa: E402
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient  # noqa: E402
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig  # noqa: E402
from graphiti_core.llm_client.config import LLMConfig  # noqa: E402
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient  # noqa: E402
from graphiti_core.nodes import EpisodeType  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NEO4J_URI        = os.getenv('NEO4J_URI',            'bolt://localhost:7687')
NEO4J_USER       = os.getenv('NEO4J_USER',           'neo4j')
NEO4J_PASSWORD   = os.getenv('NEO4J_PASSWORD',       'password')
DASHSCOPE_API_KEY  = os.getenv('DASHSCOPE_API_KEY',  '')
DASHSCOPE_BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
LLM_MODEL        = os.getenv('LLM_MODEL',            'qwen-plus')
SMALL_LLM_MODEL  = os.getenv('LLM_SMALL_MODEL',      'qwen-turbo')
EMBEDDING_MODEL  = os.getenv('LLM_EMBEDDING_MODEL',  'text-embedding-v3')

# ---------------------------------------------------------------------------
# Extraction instructions
# ---------------------------------------------------------------------------

EXTRACT_INSTRUCTION = """
This content contains observations about an ASD child receiving DIR/Floortime
intervention. Extract only meaningful, lasting facts about the child.

ENTITY EXTRACTION:
- Extract the child's name as the primary entity.
- When interest dimensions are referenced, extract them using only these
  canonical English names: Visual, Auditory, Tactile, Motor, Construction,
  Order, Cognitive, Social.

EDGE EXTRACTION:
- Focus on facts that reveal the child's characteristics, preferences,
  behavioral patterns, or intervention outcomes. Skip transient or
  situational details.
- For child-dimension relationships, include emotional valence in the fact:
  strongly positive (主动参与/高度热情), mildly positive (接受/探索),
  neutral, mildly negative (被动/回避倾向), strongly negative (明显回避/焦虑).
- When a fact signals a change from a prior pattern, state it explicitly
  so outdated facts can be superseded.
"""

# ---------------------------------------------------------------------------
# FIFO Queue 数据结构
# ---------------------------------------------------------------------------

@dataclass
class QueuedEpisode:
    """队列中的一个待处理记忆片段。"""
    id: str                  = field(default_factory=lambda: str(uuid4()))
    episode_name: str        = ''
    content: str             = ''
    reference_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    safe_group_id: str       = ''
    queued_at: datetime      = field(default_factory=lambda: datetime.now(timezone.utc))


# 全局队列状态（asyncio 单线程安全）
_episode_queue:   asyncio.Queue      = asyncio.Queue()   # 驱动 worker 的任务队列
_pending_buffer:  list[QueuedEpisode] = []               # 已入队但未写入 graphiti，供 search 读取
_worker_task:     asyncio.Task | None = None

# ---------------------------------------------------------------------------
# Queue Worker — 顺序处理，graphiti 要求 episodes 不能并发写入
# ---------------------------------------------------------------------------

async def _queue_worker() -> None:
    """
    从 _episode_queue 中逐一取出 episode，顺序写入 graphiti。
    写入完成（无论成功失败）后从 _pending_buffer 移除。
    """
    global _pending_buffer
    while True:
        episode: QueuedEpisode = await _episode_queue.get()
        try:
            if graphiti_client is not None:
                await graphiti_client.add_episode(
                    name=episode.episode_name,
                    episode_body=episode.content,
                    source=EpisodeType.text,
                    source_description='ASD intervention observation',
                    reference_time=episode.reference_time,
                    group_id=episode.safe_group_id,
                    custom_extraction_instructions=EXTRACT_INSTRUCTION,
                )
                logger.info('[queue_worker] committed: %s', episode.episode_name)
            else:
                logger.warning('[queue_worker] graphiti_client is None, skipping: %s', episode.episode_name)
        except Exception as exc:
            logger.error('[queue_worker] failed [%s]: %s', episode.episode_name, exc)
        finally:
            # 无论成功失败，移出 pending buffer（已处理或已失败）
            _pending_buffer = [e for e in _pending_buffer if e.id != episode.id]
            _episode_queue.task_done()

# ---------------------------------------------------------------------------
# Graphiti singleton + lifespan
# ---------------------------------------------------------------------------

graphiti_client: Graphiti | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global graphiti_client, _worker_task

    llm_client = OpenAIGenericClient(
        config=LLMConfig(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
            model=LLM_MODEL,
            small_model=SMALL_LLM_MODEL,
        )
    )
    embedder = OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
            embedding_model=EMBEDDING_MODEL,
        )
    )
    reranker = OpenAIRerankerClient(
        config=LLMConfig(
            api_key=DASHSCOPE_API_KEY,
            base_url=DASHSCOPE_BASE_URL,
            model=LLM_MODEL,
        )
    )
    graphiti_client = Graphiti(
        NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
    )
    await graphiti_client.build_indices_and_constraints()

    # 启动 FIFO worker
    _worker_task = asyncio.create_task(_queue_worker())
    logger.info('[lifespan] FIFO queue worker started')

    yield

    # 关闭：取消 worker
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    logger.info('[lifespan] FIFO queue worker stopped')


# ---------------------------------------------------------------------------
# group_id 规范化
# ---------------------------------------------------------------------------

_VALID_GROUP_ID = re.compile(r'^[a-zA-Z0-9_-]+$')


def sanitize_group_id(group_id: str) -> str:
    if _VALID_GROUP_ID.match(group_id):
        return group_id
    return 'grp_' + hashlib.md5(group_id.encode('utf-8')).hexdigest()[:12]


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title='ASD Memory Service', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class WriteRequest(BaseModel):
    group_id: str
    content: str
    reference_time: str  # ISO 8601


class SearchRequest(BaseModel):
    group_id: str
    query: str
    num_results: int = 10


class FactItem(BaseModel):
    text: str
    valid_at: str | None
    invalid_at: str | None
    pending: bool = False   # True = 在队列中，尚未写入 graphiti


class SearchResponse(BaseModel):
    facts: list[FactItem]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get('/healthcheck')
async def healthcheck():
    return {
        'status': 'healthy',
        'queue_pending': _episode_queue.qsize(),
        'buffer_size': len(_pending_buffer),
    }


@app.get('/api/memory/queue/status')
async def queue_status():
    """调试接口：查看当前队列状态。"""
    return {
        'queue_size': _episode_queue.qsize(),
        'pending_buffer': [
            {
                'id': e.id,
                'episode_name': e.episode_name,
                'group_id': e.safe_group_id,
                'reference_time': e.reference_time.isoformat(),
                'queued_at': e.queued_at.isoformat(),
                'content_preview': e.content[:80] + ('...' if len(e.content) > 80 else ''),
            }
            for e in _pending_buffer
        ],
    }


@app.post('/api/memory/write', status_code=202)
async def write_memory(req: WriteRequest):
    """
    将 episode 推入 FIFO 队列，立即返回 202。
    worker 按入队顺序逐一写入 graphiti（保证 graphiti 的顺序性要求）。
    """
    if graphiti_client is None:
        raise HTTPException(status_code=503, detail='Graphiti not initialised')

    try:
        reference_time = datetime.fromisoformat(req.reference_time)
        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)
    except ValueError:
        reference_time = datetime.now(timezone.utc)

    safe_group_id = sanitize_group_id(req.group_id)
    episode = QueuedEpisode(
        episode_name=f'memory-{req.reference_time}',
        content=req.content,
        reference_time=reference_time,
        safe_group_id=safe_group_id,
    )

    # 先写入 pending_buffer（立即对 search 可见），再放入 worker 队列
    _pending_buffer.append(episode)
    await _episode_queue.put(episode)

    logger.info('[write] queued: %s (queue_size=%d)', episode.episode_name, _episode_queue.qsize())
    return {
        'success': True,
        'status': 'queued',
        'episode_id': episode.id,
        'queue_position': _episode_queue.qsize(),
    }


@app.post('/api/memory/search', response_model=SearchResponse)
async def search_memory(req: SearchRequest):
    """
    搜索记忆 = graphiti 已处理 facts（精炼） + pending buffer 原文（完整但未提取）。

    pending 在前：代表最新的、尚未被 graphiti 提炼的原始观察。
    graphiti 在后：代表经过实体提取、去重、时序建模的精炼事实。
    """
    if graphiti_client is None:
        raise HTTPException(status_code=503, detail='Graphiti not initialised')

    safe_group_id = sanitize_group_id(req.group_id)

    # ── 1. graphiti 已处理 facts ──
    edges = await graphiti_client.search(
        req.query,
        group_ids=[safe_group_id],
        num_results=req.num_results,
    )
    graphiti_facts = [
        FactItem(
            text=edge.fact,
            valid_at=edge.valid_at.isoformat() if edge.valid_at else None,
            invalid_at=edge.invalid_at.isoformat() if edge.invalid_at else None,
            pending=False,
        )
        for edge in edges
    ]

    # ── 2. pending buffer — 仅属于本 group 的条目 ──
    pending_facts = [
        FactItem(
            text=ep.content,
            valid_at=ep.reference_time.isoformat(),
            invalid_at=None,
            pending=True,
        )
        for ep in _pending_buffer
        if ep.safe_group_id == safe_group_id
    ]

    # pending 在前（最新原始观察），graphiti 在后（历史精炼事实）
    return SearchResponse(facts=pending_facts + graphiti_facts)
