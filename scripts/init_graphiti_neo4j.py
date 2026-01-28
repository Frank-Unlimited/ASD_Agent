"""
初始化 Graphiti 所需的 Neo4j 索引
使用 Graphiti 的官方方法
"""
import asyncio
import os
from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7688")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
LLM_SMALL_MODEL = os.getenv("LLM_SMALL_MODEL", "qwen-flash")
LLM_EMBEDDING_MODEL = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-v3")
LLM_EMBEDDING_DIM = int(os.getenv("LLM_EMBEDDING_DIM", "1536"))

# 为 Graphiti 的 reranker 设置环境变量
os.environ['OPENAI_API_KEY'] = LLM_API_KEY


async def init_graphiti():
    """使用 Graphiti 官方方法初始化索引"""
    print("正在初始化 Graphiti...")
    
    # 配置 LLM（使用统一配置）
    llm_config = LLMConfig(
        api_key=LLM_API_KEY,
        model=LLM_MODEL,
        small_model=LLM_SMALL_MODEL,
        base_url=LLM_BASE_URL
    )
    llm_client = OpenAIGenericClient(config=llm_config)
    
    # 配置 Embedder
    embedder_config = OpenAIEmbedderConfig(
        api_key=LLM_API_KEY,
        embedding_model=LLM_EMBEDDING_MODEL,
        embedding_dim=LLM_EMBEDDING_DIM,
        base_url=LLM_BASE_URL
    )
    embedder = OpenAIEmbedder(config=embedder_config)
    
    # 创建 Graphiti 客户端
    graphiti = Graphiti(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        llm_client=llm_client,
        embedder=embedder
    )
    
    try:
        print("正在创建索引和约束...")
        await graphiti.build_indices_and_constraints()
        print("✅ 索引和约束创建成功！")
        
        # 验证连接
        print("\n正在验证 Neo4j 连接...")
        await graphiti.driver.health_check()
        print("✅ Neo4j 连接正常！")
        
    finally:
        await graphiti.close()
    
    print("\n✅ Graphiti 初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_graphiti())

