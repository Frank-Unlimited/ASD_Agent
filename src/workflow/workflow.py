"""
LangGraph 工作流
实现完整的 7 步闭环流程
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.models.state import DynamicInterventionState
from src.container import container


# ============ 节点函数定义 ============

async def assessment_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    评估节点（第一步）
    职责：解析报告/量表，构建孩子画像
    """
    print("\n[Node] 评估节点执行中...")
    
    # 从容器获取服务
    document_parser = container.get('document_parser')
    assessment_service = container.get('assessment')
    sqlite_service = container.get('sqlite')
    
    # 假设从 tempData 中获取报告路径
    report_path = state.get('tempData', {}).get('reportPath', '/mock/report.pdf')
    
    # 1. 解析报告
    parsed_data = await document_parser.parse_report(report_path, 'pdf')
    
    # 2. 构建画像
    portrait = await assessment_service.build_portrait(parsed_data)
    
    # 3. 保存到数据库
    child_profile = {
        "childId": state['childTimeline']['profile']['childId'],
        "name": state['childTimeline']['profile']['name'],
        "portrait": portrait
    }
    await sqlite_service.save_child(child_profile)
    
    # 4. 更新 State
    return {
        "childTimeline": {
            **state['childTimeline'],
            "profile": {**state['childTimeline']['profile'], **child_profile}
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "assessment",
            "nextNode": "weekly_plan"
        }
    }


async def weekly_plan_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    周计划生成节点（第二步）
    职责：生成个性化周计划
    """
    print("\n[Node] 周计划生成节点执行中...")
    
    # 从容器获取服务
    weekly_plan_service = container.get('weekly_plan')
    graphiti_service = container.get('graphiti')
    sqlite_service = container.get('sqlite')
    
    child_id = state['childTimeline']['profile']['childId']
    
    # 1. 从 Graphiti 构建上下文（缓存到 State）
    current_context = await graphiti_service.build_context(child_id)
    
    # 2. 生成周计划
    weekly_plan = await weekly_plan_service.generate_weekly_plan(
        child_id=child_id,
        child_profile=state['childTimeline']['profile'],
        current_context=current_context
    )
    
    # 3. 保存周计划
    plan_id = await sqlite_service.save_weekly_plan(weekly_plan)
    weekly_plan['planId'] = plan_id
    
    # 4. 更新 State
    return {
        "currentContext": current_context,
        "currentWeeklyPlan": weekly_plan,
        "workflow": {
            **state['workflow'],
            "currentNode": "weekly_plan",
            "nextNode": "game_start"
        }
    }


async def game_start_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    游戏开始节点（第三步）
    职责：创建会话，初始化会话数据
    """
    print("\n[Node] 游戏开始节点执行中...")
    
    sqlite_service = container.get('sqlite')
    
    child_id = state['childTimeline']['profile']['childId']
    game_id = state.get('tempData', {}).get('gameId', 'game-001')
    
    # 1. 创建会话
    session_id = await sqlite_service.create_session(child_id, game_id)
    
    # 2. 更新 State
    return {
        "currentSession": {
            "sessionId": session_id,
            "gameId": game_id,
            "status": "in_progress",
            "quickObservations": [],
            "voiceObservations": []
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "game_start",
            "nextNode": "game_end"  # 简化流程，直接跳到结束
        }
    }


async def game_end_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    游戏结束节点
    职责：标记会话结束
    """
    print("\n[Node] 游戏结束节点执行中...")
    
    sqlite_service = container.get('sqlite')
    
    session_id = state['currentSession']['sessionId']
    
    # 1. 更新会话状态
    await sqlite_service.update_session(session_id, {"status": "ended"})
    
    # 2. 更新 State
    return {
        "currentSession": {
            **state['currentSession'],
            "status": "ended"
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "game_end",
            "nextNode": "preliminary_summary"
        }
    }


async def preliminary_summary_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    初步总结节点（第四步）
    职责：生成初步总结
    """
    print("\n[Node] 初步总结节点执行中...")
    
    summary_service = container.get('summary')
    
    session_id = state['currentSession']['sessionId']
    
    # 1. 生成初步总结（从 State 读取历史数据，不重复查询）
    preliminary_summary = await summary_service.generate_preliminary_summary(
        session_id=session_id,
        session_data=state['currentSession'],
        historical_data=state.get('sessionHistory', [])
    )
    
    # 2. 更新 State
    return {
        "currentSession": {
            **state['currentSession'],
            "preliminarySummary": preliminary_summary
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "preliminary_summary",
            "nextNode": "feedback_form"
        }
    }


async def feedback_form_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    反馈表生成节点（第五步）
    职责：生成反馈表，进入 HITL 暂停
    """
    print("\n[Node] 反馈表生成节点执行中...")
    
    summary_service = container.get('summary')
    
    # 1. 生成反馈表
    feedback_form = await summary_service.generate_feedback_form(
        state['currentSession']['preliminarySummary']
    )
    
    # 2. 更新 State，标记为 HITL 暂停
    return {
        "currentSession": {
            **state['currentSession'],
            "feedbackForm": feedback_form
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "feedback_form",
            "nextNode": "hitl_pause",
            "isHITLPaused": True
        }
    }


async def final_summary_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    最终总结节点（第七步，家长提交反馈后）
    职责：融合所有数据，生成最终总结
    """
    print("\n[Node] 最终总结节点执行中...")
    
    summary_service = container.get('summary')
    
    session_id = state['currentSession']['sessionId']
    
    # 1. 生成最终总结
    final_summary = await summary_service.generate_final_summary(
        session_id=session_id,
        all_data=state['currentSession'],
        parent_feedback=state['currentSession'].get('parentFeedback', {})
    )
    
    # 2. 更新 State
    return {
        "currentSession": {
            **state['currentSession'],
            "finalSummary": final_summary
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "final_summary",
            "nextNode": "memory_update",
            "isHITLPaused": False
        }
    }


async def memory_update_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    记忆更新节点（第六步）
    职责：批量写入 Graphiti，刷新上下文
    """
    print("\n[Node] 记忆更新节点执行中...")
    
    memory_update_service = container.get('memory_update')
    
    child_id = state['childTimeline']['profile']['childId']
    
    # 1. 更新记忆（批量写入）
    await memory_update_service.update_memory(
        child_id=child_id,
        session_data=state['currentSession']
    )
    
    # 2. 刷新上下文
    new_context = await memory_update_service.refresh_context(child_id)
    
    # 3. 更新 State
    return {
        "currentContext": new_context,
        "workflow": {
            **state['workflow'],
            "currentNode": "memory_update",
            "nextNode": "reassessment"
        }
    }


async def reassessment_node(state: DynamicInterventionState) -> Dict[str, Any]:
    """
    再评估节点（第六步）
    职责：重新评估孩子，判断是否需要调整计划
    """
    print("\n[Node] 再评估节点执行中...")
    
    reassessment_service = container.get('reassessment')
    
    child_id = state['childTimeline']['profile']['childId']
    
    # 1. 再评估
    reassessment_result = await reassessment_service.reassess_child(
        child_id=child_id,
        session_data=state['currentSession'],
        current_context=state['currentContext']
    )
    
    # 2. 更新画像
    updated_portrait = await reassessment_service.update_portrait(
        child_id=child_id,
        reassessment_result=reassessment_result
    )
    
    # 3. 检查是否需要调整
    needs_adjustment = await reassessment_service.check_adjustment_needed(
        reassessment_result
    )
    
    # 4. 更新 State
    return {
        "childTimeline": {
            **state['childTimeline'],
            "profile": {**state['childTimeline']['profile'], **updated_portrait}
        },
        "workflow": {
            **state['workflow'],
            "currentNode": "reassessment",
            "nextNode": "weekly_plan" if needs_adjustment else "end",
            "needsAdjustment": needs_adjustment
        }
    }


# ============ 条件边函数 ============

def should_adjust_plan(state: DynamicInterventionState) -> str:
    """
    条件边：判断是否需要调整计划
    """
    needs_adjustment = state['workflow'].get('needsAdjustment', False)
    
    if needs_adjustment:
        print("[Condition] 需要调整计划，返回周计划节点")
        return "weekly_plan"
    else:
        print("[Condition] 不需要调整，流程结束")
        return "end"


# ============ 构建工作流 ============

def create_intervention_workflow() -> StateGraph:
    """
    创建干预工作流
    """
    # 创建状态图
    workflow = StateGraph(DynamicInterventionState)
    
    # 添加节点
    workflow.add_node("assessment", assessment_node)
    workflow.add_node("weekly_plan", weekly_plan_node)
    workflow.add_node("game_start", game_start_node)
    workflow.add_node("game_end", game_end_node)
    workflow.add_node("preliminary_summary", preliminary_summary_node)
    workflow.add_node("feedback_form", feedback_form_node)
    workflow.add_node("final_summary", final_summary_node)
    workflow.add_node("memory_update", memory_update_node)
    workflow.add_node("reassessment", reassessment_node)
    
    # 添加边
    workflow.add_edge("assessment", "weekly_plan")
    workflow.add_edge("weekly_plan", "game_start")
    workflow.add_edge("game_start", "game_end")
    workflow.add_edge("game_end", "preliminary_summary")
    workflow.add_edge("preliminary_summary", "feedback_form")
    workflow.add_edge("feedback_form", "final_summary")  # HITL 暂停后恢复
    workflow.add_edge("final_summary", "memory_update")
    workflow.add_edge("memory_update", "reassessment")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "reassessment",
        should_adjust_plan,
        {
            "weekly_plan": "weekly_plan",
            "end": END
        }
    )
    
    # 设置入口点
    workflow.set_entry_point("assessment")
    
    return workflow


# ============ 编译工作流 ============

def get_compiled_workflow():
    """
    获取编译后的工作流
    """
    workflow = create_intervention_workflow()
    return workflow.compile()
