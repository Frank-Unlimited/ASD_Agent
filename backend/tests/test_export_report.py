"""
测试评估报告导出
"""
import requests

BASE_URL = "http://localhost:8000"


def test_export_json():
    """测试导出 JSON 格式"""
    print("\n" + "="*60)
    print("测试导出 JSON 格式")
    print("="*60)
    
    # 先获取一个评估ID
    response = requests.post(
        f"{BASE_URL}/api/assessment/history",
        json={"child_id": "test_child_001", "limit": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['assessments']:
            assessment_id = data['assessments'][0]['assessment_id']
            print(f"\n使用评估ID: {assessment_id}")
            
            # 导出 JSON
            export_response = requests.get(
                f"{BASE_URL}/api/assessment/{assessment_id}/export?format=json"
            )
            
            if export_response.status_code == 200:
                print(f"\n✅ JSON 导出成功")
                print(f"数据大小: {len(export_response.content)} bytes")
                
                # 保存到文件
                with open("assessment_export.json", "w", encoding="utf-8") as f:
                    f.write(export_response.text)
                print(f"已保存到: assessment_export.json")
            else:
                print(f"❌ 导出失败: {export_response.status_code}")
        else:
            print("❌ 没有找到评估记录")
    else:
        print(f"❌ 获取评估历史失败: {response.status_code}")


def test_export_markdown():
    """测试导出 Markdown 格式"""
    print("\n" + "="*60)
    print("测试导出 Markdown 格式")
    print("="*60)
    
    # 先获取一个评估ID
    response = requests.post(
        f"{BASE_URL}/api/assessment/history",
        json={"child_id": "test_child_001", "limit": 1}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['assessments']:
            assessment_id = data['assessments'][0]['assessment_id']
            print(f"\n使用评估ID: {assessment_id}")
            
            # 导出 Markdown
            export_response = requests.get(
                f"{BASE_URL}/api/assessment/{assessment_id}/export?format=markdown"
            )
            
            if export_response.status_code == 200:
                print(f"\n✅ Markdown 导出成功")
                print(f"数据大小: {len(export_response.content)} bytes")
                
                # 保存到文件
                with open("assessment_export.md", "w", encoding="utf-8") as f:
                    f.write(export_response.text)
                print(f"已保存到: assessment_export.md")
                
                # 显示前几行
                print(f"\n--- 报告预览 ---")
                lines = export_response.text.split('\n')
                for line in lines[:20]:
                    print(line)
                print("...")
            else:
                print(f"❌ 导出失败: {export_response.status_code}")
        else:
            print("❌ 没有找到评估记录")
    else:
        print(f"❌ 获取评估历史失败: {response.status_code}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("评估报告导出测试")
    print("="*60)
    
    test_export_json()
    test_export_markdown()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
