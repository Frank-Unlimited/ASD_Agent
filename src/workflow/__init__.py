"""
工作流编排
"""

def get_compiled_workflow():
    """延迟导入避免循环依赖"""
    from src.workflow.workflow import get_compiled_workflow as _get_compiled_workflow
    return _get_compiled_workflow()

def create_intervention_workflow():
    """延迟导入避免循环依赖"""
    from src.workflow.workflow import create_intervention_workflow as _create_intervention_workflow
    return _create_intervention_workflow()

__all__ = [
    'create_intervention_workflow',
    'get_compiled_workflow',
]

