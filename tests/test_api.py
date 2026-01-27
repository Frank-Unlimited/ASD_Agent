#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LangGraph API 快速测试脚本
"""
import sys
import io
import requests
import json
import time

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:7860"

def test_workflow():
    """测试完整工作流"""
    print("=" * 60)
    print("LangGraph 工作流测试")
    print("=" * 60)

    # 1. 初始化工作流
    print("\n[1/10] 初始化工作流...")
    init_response = requests.post(f"{API_BASE}/api/workflow/init", json={
        "childId": "child-001",
        "childName": "辰辰",
        "reportPath": "/mock/report.pdf",
        "gameId": "game-001"
    })

    if not init_response.ok:
        print(f"❌ 初始化失败: {init_response.text}")
        return

    init_data = init_response.json()
    workflow_id = init_data["workflowId"]
    print(f"✅ 工作流ID: {workflow_id}")

    # 2. 执行所有节点
    nodes = [
        "assessment",
        "weekly_plan",
        "game_start",
        "game_end",
        "preliminary_summary",
        "feedback_form",
        "final_summary",
        "memory_update",
        "reassessment"
    ]

    for i, node in enumerate(nodes, 2):
        print(f"\n[{i}/10] 执行节点: {node}...")

        exec_response = requests.post(
            f"{API_BASE}/api/workflow/{workflow_id}/execute/{node}"
        )

        if not exec_response.ok:
            print(f"❌ 节点执行失败: {exec_response.text}")
            return

        exec_data = exec_response.json()
        print(f"✅ 执行成功 (耗时: {exec_data.get('executionTime', 0):.2f}s)")
        print(f"   当前节点: {exec_data.get('currentNode')}")
        print(f"   下一节点: {exec_data.get('nextNode')}")

        # 在 feedback_form 节点后提交反馈
        if node == "feedback_form":
            print("\n[HITL] 提交家长反馈...")
            feedback_response = requests.post(
                f"{API_BASE}/api/workflow/{workflow_id}/submit-feedback",
                json={
                    "feedback": {
                        "feeling": "孩子今天特别开心，互动很积极",
                        "progress": "主动发起了3次互动，比上次多了",
                        "difficulty": "注意力容易分散，需要多次引导"
                    }
                }
            )

            if feedback_response.ok:
                print("✅ 反馈提交成功")
            else:
                print(f"❌ 反馈提交失败: {feedback_response.text}")

        time.sleep(0.5)  # 短暂延迟

    # 3. 获取最终状态
    print("\n[10/10] 获取最终状态...")
    status_response = requests.get(f"{API_BASE}/api/workflow/{workflow_id}/status")

    if status_response.ok:
        status_data = status_response.json()
        print("✅ 最终状态:")
        print(f"   孩子: {status_data['state']['childTimeline']['profile']['name']}")
        print(f"   当前节点: {status_data['currentNode']}")

        # 显示部分 State 数据
        state = status_data['state']
        if 'currentWeeklyPlan' in state and state['currentWeeklyPlan']:
            print(f"   周计划ID: {state['currentWeeklyPlan'].get('planId')}")
        if 'currentSession' in state and state['currentSession']:
            print(f"   会话ID: {state['currentSession'].get('sessionId')}")

    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        # 检查服务是否运行
        health = requests.get(f"{API_BASE}/health", timeout=2)
        if health.ok:
            print("✅ 后端服务正常运行")
            test_workflow()
        else:
            print("❌ 后端服务异常")
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print(f"   请确保服务正在运行: python -m src.main")
