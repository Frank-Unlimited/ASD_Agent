"""
Cypher 查询构建器
用于构建复杂的 Neo4j Cypher 查询
"""
from typing import Dict, List, Any, Optional


class QueryBuilder:
    """Cypher 查询构建器"""
    
    @staticmethod
    def build_match_clause(
        node_label: str,
        properties: Optional[Dict[str, Any]] = None,
        variable: str = "n"
    ) -> str:
        """
        构建 MATCH 子句
        
        Args:
            node_label: 节点标签
            properties: 节点属性过滤
            variable: 节点变量名
            
        Returns:
            MATCH 子句字符串
        """
        if properties:
            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            return f"MATCH ({variable}:{node_label} {{{props_str}}})"
        else:
            return f"MATCH ({variable}:{node_label})"
    
    @staticmethod
    def build_where_clause(conditions: List[str]) -> str:
        """
        构建 WHERE 子句
        
        Args:
            conditions: 条件列表
            
        Returns:
            WHERE 子句字符串
        """
        if not conditions:
            return ""
        return "WHERE " + " AND ".join(conditions)
    
    @staticmethod
    def build_create_node(
        node_label: str,
        properties: Dict[str, Any],
        variable: str = "n"
    ) -> str:
        """
        构建 CREATE 节点语句
        
        Args:
            node_label: 节点标签
            properties: 节点属性
            variable: 节点变量名
            
        Returns:
            CREATE 语句字符串
        """
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        return f"CREATE ({variable}:{node_label} {{{props_str}}})"
    
    @staticmethod
    def build_merge_node(
        node_label: str,
        match_properties: Dict[str, Any],
        set_properties: Optional[Dict[str, Any]] = None,
        variable: str = "n"
    ) -> str:
        """
        构建 MERGE 节点语句
        
        Args:
            node_label: 节点标签
            match_properties: 匹配属性
            set_properties: 设置属性（ON CREATE/ON MATCH）
            variable: 节点变量名
            
        Returns:
            MERGE 语句字符串
        """
        match_props_str = ", ".join([f"{k}: ${k}" for k in match_properties.keys()])
        query = f"MERGE ({variable}:{node_label} {{{match_props_str}}})"
        
        if set_properties:
            set_props_str = ", ".join([f"{variable}.{k} = ${k}" for k in set_properties.keys()])
            query += f"\nON CREATE SET {set_props_str}"
        
        return query
    
    @staticmethod
    def build_create_relationship(
        from_var: str,
        to_var: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None,
        rel_var: str = "r"
    ) -> str:
        """
        构建 CREATE 关系语句
        
        Args:
            from_var: 起始节点变量
            to_var: 目标节点变量
            rel_type: 关系类型
            properties: 关系属性
            rel_var: 关系变量名
            
        Returns:
            CREATE 关系语句字符串
        """
        if properties:
            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            return f"CREATE ({from_var})-[{rel_var}:{rel_type} {{{props_str}}}]->({to_var})"
        else:
            return f"CREATE ({from_var})-[{rel_var}:{rel_type}]->({to_var})"
    
    @staticmethod
    def build_merge_relationship(
        from_var: str,
        to_var: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None,
        rel_var: str = "r"
    ) -> str:
        """
        构建 MERGE 关系语句
        
        Args:
            from_var: 起始节点变量
            to_var: 目标节点变量
            rel_type: 关系类型
            properties: 关系属性
            rel_var: 关系变量名
            
        Returns:
            MERGE 关系语句字符串
        """
        if properties:
            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            return f"MERGE ({from_var})-[{rel_var}:{rel_type} {{{props_str}}}]->({to_var})"
        else:
            return f"MERGE ({from_var})-[{rel_var}:{rel_type}]->({to_var})"
    
    @staticmethod
    def build_return_clause(
        variables: List[str],
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> str:
        """
        构建 RETURN 子句
        
        Args:
            variables: 返回变量列表
            order_by: 排序字段
            limit: 限制数量
            skip: 跳过数量
            
        Returns:
            RETURN 子句字符串
        """
        query = "RETURN " + ", ".join(variables)
        
        if order_by:
            query += f"\nORDER BY {order_by}"
        
        if skip:
            query += f"\nSKIP {skip}"
        
        if limit:
            query += f"\nLIMIT {limit}"
        
        return query
