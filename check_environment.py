"""
环境检查脚本
检查所有依赖是否正确安装
"""
import sys

def check_imports():
    """检查所有必要的导入"""
    checks = []
    
    # 核心依赖
    try:
        import graphiti_core
        version = getattr(graphiti_core, '__version__', 'installed')
        checks.append(("[OK]", "graphiti-core", version))
    except ImportError as e:
        checks.append(("[FAIL]", "graphiti-core", f"not installed: {e}"))
    
    try:
        import neo4j
        version = getattr(neo4j, '__version__', 'installed')
        checks.append(("[OK]", "neo4j", version))
    except ImportError as e:
        checks.append(("[FAIL]", "neo4j", f"not installed: {e}"))
    
    try:
        import langgraph
        version = getattr(langgraph, '__version__', 'installed')
        checks.append(("[OK]", "langgraph", version))
    except ImportError as e:
        checks.append(("[FAIL]", "langgraph", f"not installed: {e}"))
    
    try:
        import langchain
        version = getattr(langchain, '__version__', 'installed')
        checks.append(("[OK]", "langchain", version))
    except ImportError as e:
        checks.append(("[FAIL]", "langchain", f"not installed: {e}"))
    
    try:
        import fastapi
        version = getattr(fastapi, '__version__', 'installed')
        checks.append(("[OK]", "fastapi", version))
    except ImportError as e:
        checks.append(("[FAIL]", "fastapi", f"not installed: {e}"))
    
    try:
        import uvicorn
        version = getattr(uvicorn, '__version__', 'installed')
        checks.append(("[OK]", "uvicorn", version))
    except ImportError as e:
        checks.append(("[FAIL]", "uvicorn", f"not installed: {e}"))
    
    try:
        import openai
        version = getattr(openai, '__version__', 'installed')
        checks.append(("[OK]", "openai", version))
    except ImportError as e:
        checks.append(("[FAIL]", "openai", f"not installed: {e}"))
    
    try:
        import anthropic
        version = getattr(anthropic, '__version__', 'installed')
        checks.append(("[OK]", "anthropic", version))
    except ImportError as e:
        checks.append(("[FAIL]", "anthropic", f"not installed: {e}"))
    
    try:
        import sqlalchemy
        version = getattr(sqlalchemy, '__version__', 'installed')
        checks.append(("[OK]", "sqlalchemy", version))
    except ImportError as e:
        checks.append(("[FAIL]", "sqlalchemy", f"not installed: {e}"))
    
    try:
        import pydantic
        version = getattr(pydantic, '__version__', 'installed')
        checks.append(("[OK]", "pydantic", version))
    except ImportError as e:
        checks.append(("[FAIL]", "pydantic", f"not installed: {e}"))
    
    return checks


def check_project_structure():
    """检查项目结构"""
    import os
    
    required_dirs = [
        "src",
        "services",
        "services/real",
        "services/mock",
        "tests",
        "data"
    ]
    
    checks = []
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        status = "[OK]" if exists else "[FAIL]"
        checks.append((status, dir_path, "exists" if exists else "missing"))
    
    return checks


def check_services():
    """检查服务是否可以导入"""
    checks = []
    
    try:
        from src.container import container
        checks.append(("[OK]", "container", "import success"))
    except Exception as e:
        checks.append(("[FAIL]", "container", f"import failed: {e}"))
    
    try:
        from services.real.graphiti_service import GraphitiService
        checks.append(("[OK]", "GraphitiService", "import success"))
    except Exception as e:
        checks.append(("[FAIL]", "GraphitiService", f"import failed: {e}"))
    
    try:
        from services.real.llm_service import DeepSeekLLMService
        checks.append(("[OK]", "DeepSeekLLMService", "import success"))
    except Exception as e:
        checks.append(("[FAIL]", "DeepSeekLLMService", f"import failed: {e}"))
    
    try:
        from services.mock.graphiti_service import MockGraphitiService
        checks.append(("[OK]", "MockGraphitiService", "import success"))
    except Exception as e:
        checks.append(("[FAIL]", "MockGraphitiService", f"import failed: {e}"))
    
    try:
        from src.langgraph.workflow import get_compiled_workflow
        checks.append(("[OK]", "LangGraph Workflow", "import success"))
    except Exception as e:
        checks.append(("[FAIL]", "LangGraph Workflow", f"import failed: {e}"))
    
    return checks


def check_neo4j_connection():
    """检查 Neo4j 连接"""
    try:
        from neo4j import GraphDatabase
        from src.config import settings
        
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1 as num")
            record = result.single()
            if record and record["num"] == 1:
                driver.close()
                return ("[OK]", "Neo4j Connection", "success")
        
        driver.close()
        return ("[FAIL]", "Neo4j Connection", "failed")
        
    except Exception as e:
        return ("[FAIL]", "Neo4j Connection", f"failed: {str(e)[:50]}")


def main():
    print("=" * 70)
    print("ASD Agent Environment Check")
    print("=" * 70)
    
    print(f"\nPython Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    
    print("\n" + "=" * 70)
    print("1. Core Dependencies")
    print("=" * 70)
    for status, name, version in check_imports():
        print(f"{status} {name:20s} {version}")
    
    print("\n" + "=" * 70)
    print("2. Project Structure")
    print("=" * 70)
    for status, path, msg in check_project_structure():
        print(f"{status} {path:30s} {msg}")
    
    print("\n" + "=" * 70)
    print("3. Service Imports")
    print("=" * 70)
    for status, name, msg in check_services():
        print(f"{status} {name:30s} {msg}")
    
    print("\n" + "=" * 70)
    print("4. Neo4j Connection")
    print("=" * 70)
    status, name, msg = check_neo4j_connection()
    print(f"{status} {name:30s} {msg}")
    
    print("\n" + "=" * 70)
    print("Check Complete")
    print("=" * 70)
    
    # Statistics
    all_checks = (
        check_imports() + 
        check_project_structure() + 
        check_services() + 
        [check_neo4j_connection()]
    )
    
    success_count = sum(1 for check in all_checks if check[0] in ["OK", "[OK]"])
    total_count = len(all_checks)
    
    print(f"\nPassed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("\nAll checks passed! Environment is ready.")
    else:
        print(f"\n{total_count - success_count} checks failed. See details above.")


if __name__ == "__main__":
    main()
