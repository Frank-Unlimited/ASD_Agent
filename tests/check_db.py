import sqlite3

conn = sqlite3.connect('data/asd_intervention.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 查看游戏方案
print("\n检查是否有 game_plans 表...")
if ('game_plans',) in tables:
    cursor.execute("SELECT game_id FROM game_plans")
    plans = cursor.fetchall()
    print(f"游戏方案数量: {len(plans)}")
    for plan in plans:
        print(f"  - {plan[0]}")
else:
    print("❌ 没有 game_plans 表")

conn.close()
