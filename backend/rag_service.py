"""
阿里云百炼 RAG 知识库检索服务

提供知识库检索 API，供前端调用。
使用阿里云百炼 SDK 的 Retrieve 接口检索文档搜索类知识库。

Run: uvicorn rag_service:app --port 8001 --reload
或集成到 memory_service.py 中复用端口 8000
"""

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

# 尝试导入阿里云 SDK
try:
    from alibabacloud_bailian20231229.client import Client as BailianClient
    from alibabacloud_bailian20231229 import models as bailian_models
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_credentials.client import Client as CredentialClient
    SDK_AVAILABLE = True
except ImportError:
    logger.warning(
        "阿里云百炼 SDK 未安装。请运行: pip install alibabacloud-bailian20231229"
    )
    SDK_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORKSPACE_ID = os.getenv('ALIBABA_WORKSPACE_ID', '')
DEFAULT_INDEX_ID = os.getenv('ALIBABA_INDEX_ID', '')

# ---------------------------------------------------------------------------
# Bailian Client
# ---------------------------------------------------------------------------

bailian_client: Optional[Any] = None


def create_bailian_client() -> Optional[Any]:
    """创建阿里云百炼客户端"""
    if not SDK_AVAILABLE:
        logger.warning("SDK 不可用，无法创建客户端")
        return None
    
    try:
        # 使用环境变量中的 AccessKey 凭据
        credential = CredentialClient()
        config = open_api_models.Config(
            credential=credential,
            endpoint='bailian.cn-beijing.aliyuncs.com'
        )
        client = BailianClient(config)
        logger.info("阿里云百炼客户端初始化成功")
        return client
    except Exception as e:
        logger.error(f"创建阿里云百炼客户端失败: {e}")
        return None


# 初始化客户端
bailian_client = create_bailian_client()

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title='ASD RAG Service', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class RAGSearchRequest(BaseModel):
    query: str
    index_id: Optional[str] = None  # 如果不传，使用默认知识库 ID
    top_k: int = 5
    enable_reranking: bool = False  # 默认关闭重排序（SDK 参数问题）
    rerank_min_score: float = 0.20
    dense_similarity_top_k: int = 50
    sparse_similarity_top_k: int = 50


class RAGNode(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]


class RAGSearchResponse(BaseModel):
    nodes: List[RAGNode]
    success: bool
    message: Optional[str] = None
    request_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get('/healthcheck')
async def healthcheck():
    """健康检查"""
    return {
        'status': 'healthy',
        'sdk_available': SDK_AVAILABLE,
        'client_ready': bailian_client is not None,
        'workspace_id': WORKSPACE_ID[:10] + '...' if WORKSPACE_ID else None,
        'default_index_id': DEFAULT_INDEX_ID[:10] + '...' if DEFAULT_INDEX_ID else None,
    }


@app.post('/api/rag/search', response_model=RAGSearchResponse)
async def search_rag(request: RAGSearchRequest):
    """
    检索阿里云百炼知识库
    
    Args:
        request: 检索请求，包含查询文本、知识库 ID、Top K 等参数
    
    Returns:
        RAGSearchResponse: 检索结果，包含文本切片列表
    """
    if not SDK_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail='阿里云百炼 SDK 未安装'
        )
    
    if bailian_client is None:
        raise HTTPException(
            status_code=503,
            detail='阿里云百炼客户端未初始化'
        )
    
    if not WORKSPACE_ID:
        raise HTTPException(
            status_code=500,
            detail='ALIBABA_WORKSPACE_ID 未配置'
        )
    
    # 使用传入的 index_id 或默认值
    index_id = request.index_id or DEFAULT_INDEX_ID
    if not index_id:
        raise HTTPException(
            status_code=400,
            detail='知识库 ID 未指定且未配置默认值'
        )
    
    try:
        logger.info(f"[RAG Search] 查询: {request.query}, Index: {index_id}")
        
        # 构建 Retrieve 请求
        retrieve_request = bailian_models.RetrieveRequest()
        retrieve_request.query = request.query
        retrieve_request.index_id = index_id
        retrieve_request.dense_similarity_top_k = request.dense_similarity_top_k
        retrieve_request.sparse_similarity_top_k = request.sparse_similarity_top_k
        retrieve_request.enable_reranking = request.enable_reranking
        
        # 如果启用重排序，添加重排序配置
        if request.enable_reranking:
            rerank_config = bailian_models.RetrieveRequestRerank()
            # 尝试使用属性设置
            if hasattr(rerank_config, 'rerank_min_score'):
                rerank_config.rerank_min_score = request.rerank_min_score
            if hasattr(rerank_config, 'rerank_top_n'):
                rerank_config.rerank_top_n = request.top_k
            retrieve_request.rerank = [rerank_config]
        
        # 调用 Retrieve API
        response = bailian_client.retrieve(WORKSPACE_ID, retrieve_request)
        
        # 检查响应
        if not response.body.success:
            logger.warning(f"[RAG Search] 失败: {response.body.message}")
            return RAGSearchResponse(
                nodes=[],
                success=False,
                message=response.body.message,
                request_id=response.body.request_id,
            )
        
        # 转换结果
        nodes = []
        if response.body.data and response.body.data.nodes:
            for node in response.body.data.nodes:
                nodes.append(RAGNode(
                    text=node.text or '',
                    score=node.score or 0.0,
                    metadata=node.metadata or {},
                ))
        
        logger.info(f"[RAG Search] 成功返回 {len(nodes)} 个结果")
        
        return RAGSearchResponse(
            nodes=nodes,
            success=True,
            request_id=response.body.request_id,
        )
        
    except Exception as e:
        logger.error(f"[RAG Search] 异常: {str(e)}")
        return RAGSearchResponse(
            nodes=[],
            success=False,
            message=str(e),
        )


@app.get('/api/rag/info')
async def rag_info():
    """获取 RAG 服务配置信息（调试用）"""
    return {
        'workspace_id': WORKSPACE_ID,
        'default_index_id': DEFAULT_INDEX_ID,
        'sdk_available': SDK_AVAILABLE,
        'client_ready': bailian_client is not None,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
