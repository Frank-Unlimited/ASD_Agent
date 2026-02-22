"""清空 Neo4j 数据库"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7688', auth=('neo4j', 'password'))

with driver.session() as session:
    session.run('MATCH (n) DETACH DELETE n')
    print('数据库已清空')

driver.close()
