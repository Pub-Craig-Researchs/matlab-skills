"""
SQLite 混合缓存引擎 - 双轨读取机制
实现 Read-Through Cache 策略,存储本地物理路径索引与高频函数的 Markdown 缓存文本
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def get_connection(db_path: Path):
    """
    获取数据库连接的上下文管理器
    
    Args:
        db_path: SQLite 数据库文件路径
        
    Yields:
        sqlite3.Connection 对象
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # 支持字典式访问
    conn.execute("PRAGMA journal_mode=WAL")  # 启用 WAL 模式提升并发性能
    conn.execute("PRAGMA synchronous=NORMAL")  # 平衡性能与安全性
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path) -> None:
    """
    初始化数据库,创建必要的数据表
    
    Args:
        db_path: SQLite 数据库文件路径
    """
    with get_connection(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS docs (
                name TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_name ON docs(name);
            CREATE INDEX IF NOT EXISTS idx_updated ON docs(updated_at);
        """)
        conn.commit()
        logger.info(f"数据库初始化完成: {db_path}")


def lookup_function(conn: sqlite3.Connection, func_name: str) -> Optional[Tuple[Optional[str], str]]:
    """
    查询函数文档
    
    Args:
        conn: 数据库连接
        func_name: 函数名称
        
    Returns:
        (content, path) 元组,如果不存在则返回 None
        - content: Markdown 缓存内容 (可能为 None 表示未解析)
        - path: HTML 文件绝对路径
    """
    cursor = conn.execute(
        "SELECT content, path FROM docs WHERE name = ?",
        (func_name.lower(),)
    )
    row = cursor.fetchone()
    
    if row:
        return (row["content"], row["path"])
    
    return None


def cache_content(conn: sqlite3.Connection, func_name: str, content: str) -> None:
    """
    回写 Markdown 缓存内容
    
    Args:
        conn: 数据库连接
        func_name: 函数名称
        content: Markdown 内容
    """
    conn.execute(
        """UPDATE docs 
           SET content = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE name = ?""",
        (content, func_name.lower())
    )
    conn.commit()
    logger.debug(f"缓存已更新: {func_name}")


def batch_insert_paths(conn: sqlite3.Connection, paths: Dict[str, str]) -> int:
    """
    批量插入函数路径索引
    
    Args:
        conn: 数据库连接
        paths: {函数名: HTML路径} 字典
        
    Returns:
        插入的记录数
    """
    count = 0
    for func_name, html_path in paths.items():
        conn.execute(
            """INSERT OR REPLACE INTO docs (name, path, updated_at) 
               VALUES (?, ?, CURRENT_TIMESTAMP)""",
            (func_name.lower(), html_path)
        )
        count += 1
    
    conn.commit()
    logger.info(f"批量插入 {count} 条路径索引")
    return count


def get_stats(conn: sqlite3.Connection) -> Dict:
    """
    获取缓存统计信息
    
    Args:
        conn: 数据库连接
        
    Returns:
        统计信息字典
    """
    # 总记录数
    cursor = conn.execute("SELECT COUNT(*) as total FROM docs")
    total = cursor.fetchone()["total"]
    
    # 已缓存记录数
    cursor = conn.execute("SELECT COUNT(*) as cached FROM docs WHERE content IS NOT NULL")
    cached = cursor.fetchone()["cached"]
    
    # 未缓存记录数
    uncached = total - cached
    
    # 数据库文件大小
    cursor = conn.execute("PRAGMA page_count")
    page_count = cursor.fetchone()["page_count"]
    
    cursor = conn.execute("PRAGMA page_size")
    page_size = cursor.fetchone()["page_size"]
    
    db_size_mb = (page_count * page_size) / (1024 * 1024)
    
    return {
        "total": total,
        "cached": cached,
        "uncached": uncached,
        "cache_hit_rate": f"{(cached / total * 100):.1f}%" if total > 0 else "0%",
        "db_size_mb": f"{db_size_mb:.2f} MB"
    }


def delete_function(conn: sqlite3.Connection, func_name: str) -> bool:
    """
    删除指定函数的缓存
    
    Args:
        conn: 数据库连接
        func_name: 函数名称
        
    Returns:
        是否删除成功
    """
    cursor = conn.execute("DELETE FROM docs WHERE name = ?", (func_name.lower(),))
    conn.commit()
    return cursor.rowcount > 0


def clear_cache(conn: sqlite3.Connection) -> int:
    """
    清空所有 Markdown 缓存 (保留路径索引)
    
    Args:
        conn: 数据库连接
        
    Returns:
        清空的记录数
    """
    cursor = conn.execute("UPDATE docs SET content = NULL WHERE content IS NOT NULL")
    conn.commit()
    return cursor.rowcount


def rebuild_index(conn: sqlite3.Connection) -> None:
    """
    重建索引 (清空所有数据)
    
    Args:
        conn: 数据库连接
    """
    conn.execute("DELETE FROM docs")
    conn.commit()
    logger.info("索引已重建 (所有数据已清空)")
