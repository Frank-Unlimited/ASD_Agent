"""
测试评估 API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_generate_assessment():
    """测试生成评估"""
    print("\n" + "="*60)
    print("测试生成评估 API")
    print("="*60)
    
    # 请求数据
    request_data = {
        "child_id": "test_child_001",
        "assessment_type": "comprehensive",
        "time_range_days": 30
    }
    
    print(f"\n[1] 发送请求: POST {BASE_URL}/api/assessment/generate")
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/assessment/generate",
            json=request_data,
            timeout=180  # 3分钟超时
        )
        
        print(f"\n[2] 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 评估生成成功!")
            print(f"评估ID: {data['assessment_id']}")
            print(f"孩子ID: {data['child_id']}")
            
            # 评估报告
            report = data['report']
            print(f"\n--- 评估报告 ---")
            print(f"整体评价: {report['overall_assessment'][:200]}...")
            print(f"综合评分: {report['overall_score']}/10")
            
            # 兴趣热力图
            if 'interest_heatmap' in data and data['interest_heatmap']:
                heatmap = data['interest_heatmap']
                print(f"\n--- 兴趣热力图 ---")
                print(f"整体兴趣广度: {heatmap['overall_breadth']}")
                print(f"兴趣维度数量: {len(heatmap['dimensions'])}")
                print(f"新发现: {len(heatmap.get('new_discoveries', []))} 个")
            
            # 功能维度趋势
            if 'dimension_trends' in data and data['dimension_trends']:
                trends = data['dimension_trends']
                print(f"\n--- 功能维度趋势 ---")
                print(f"活跃维度数量: {len(trends['active_dimensions'])}")
                print(f"进步最快: {len(trends.get('top_improving', []))} 个维度")
            
            # 干预建议
            print(f"\n--- 干预建议 ---")
            for i, rec in enumerate(report['recommendations'][:3], 1):
                print(f"{i}. {rec}")
            
            return data['assessment_id']
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None


def test_get_assessment(assessment_id):
    """测试获取评估"""
    print("\n" + "="*60)
    print("测试获取评估 API")
    print("="*60)
    
    print(f"\n[1] 发送请求: GET {BASE_URL}/api/assessment/{assessment_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/assessment/{assessment_id}")
        
        print(f"\n[2] 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 评估获取成功!")
            print(f"评估ID: {data['assessment_id']}")
            print(f"评估类型: {data['assessment_type']}")
            print(f"时间: {data['timestamp']}")
            
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


def test_get_assessment_history():
    """测试获取评估历史"""
    print("\n" + "="*60)
    print("测试获取评估历史 API")
    print("="*60)
    
    request_data = {
        "child_id": "test_child_001",
        "limit": 5
    }
    
    print(f"\n[1] 发送请求: POST {BASE_URL}/api/assessment/history")
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/assessment/history",
            json=request_data
        )
        
        print(f"\n[2] 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ 评估历史获取成功!")
            print(f"孩子ID: {data['child_id']}")
            print(f"评估数量: {data['total']}")
            
            print(f"\n--- 评估历史 ---")
            for i, assessment in enumerate(data['assessments'][:3], 1):
                print(f"{i}. 评估ID: {assessment['assessment_id']}")
                print(f"   类型: {assessment['assessment_type']}")
                print(f"   时间: {assessment['timestamp']}")
            
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("评估 API 测试")
    print("="*60)
    
    # 1. 测试生成评估
    assessment_id = test_generate_assessment()
    
    if assessment_id:
        # 2. 测试获取评估
        test_get_assessment(assessment_id)
    
    # 3. 测试获取评估历史
    test_get_assessment_history()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
