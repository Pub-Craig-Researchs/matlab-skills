"""
异步多线程索引构建器 - 高并发扫描 matlab/help 目录
规避单线程 os.walk 的性能瓶颈,实现 10 万级文件的秒级扫描
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def extract_func_name(html_path: Path) -> str:
    """
    从 HTML 文件路径提取函数名
    
    Args:
        html_path: HTML 文件路径
        
    Returns:
        函数名称 (小写)
        
    Examples:
        fmincon.html -> fmincon
        ref/plot.html -> plot
    """
    # 直接提取文件名 (不含扩展名)
    func_name = html_path.stem.lower()
    
    # 过滤特殊文件 (如 index.html, toc.html 等)
    if func_name in ("index", "toc", "nav", "search"):
        return ""
    
    return func_name


def scan_directory_chunk(dir_path: Path) -> Dict[str, str]:
    """
    扫描单个目录块 (用于并发执行)
    
    Args:
        dir_path: 目录路径
        
    Returns:
        {函数名: HTML路径} 字典
    """
    result = {}
    
    try:
        if not dir_path.is_dir():
            return result
        
        # 遍历目录
        for item in dir_path.iterdir():
            if item.is_file() and item.suffix.lower() == ".html":
                func_name = extract_func_name(item)
                if func_name:
                    result[func_name] = str(item)
            elif item.is_dir():
                # 递归扫描子目录
                result.update(scan_directory_chunk(item))
    except PermissionError as e:
        logger.warning(f"权限错误,跳过目录 {dir_path}: {e}")
    except Exception as e:
        logger.error(f"扫描目录 {dir_path} 时出错: {e}")
    
    return result


def scan_help_dir(help_dir: Path, max_workers: int = 1) -> Dict[str, str]:
    """
    高并发扫描 help 目录
    
    Args:
        help_dir: MATLAB help 目录路径
        max_workers: 最大线程数 (默认 1,使用 CPU 核心数可设为 os.cpu_count())
        
    Returns:
        {函数名: HTML路径} 字典
    """
    if max_workers is None:
        max_workers = os.cpu_count() or 8
    
    if max_workers == 1:
        logger.info(f"开始扫描 help 目录 (单线程): {help_dir}")
    else:
        logger.info(f"开始扫描 help 目录: {help_dir}")
        logger.info(f"使用 {max_workers} 个并发线程")
    
    # 收集所有一级子目录
    subdirs = []
    try:
        for item in help_dir.iterdir():
            if item.is_dir():
                subdirs.append(item)
    except PermissionError as e:
        logger.error(f"无法访问 help 目录: {e}")
        return {}
    
    logger.info(f"发现 {len(subdirs)} 个子目录待扫描")
    
    # 并发扫描
    all_results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_dir = {
            executor.submit(scan_directory_chunk, subdir): subdir
            for subdir in subdirs
        }
        
        # 收集结果
        completed = 0
        for future in as_completed(future_to_dir):
            subdir = future_to_dir[future]
            completed += 1
            
            try:
                result = future.result()
                all_results.update(result)
                
                if completed % 10 == 0 or completed == len(subdirs):
                    logger.info(f"扫描进度: {completed}/{len(subdirs)} 子目录, 已发现 {len(all_results)} 个函数")
            except Exception as e:
                logger.error(f"扫描 {subdir} 时发生异常: {e}")
    
    logger.info(f"扫描完成,共发现 {len(all_results)} 个函数")
    return all_results


def bootstrap_index(conn, help_dir: Path, max_workers: int = 1) -> int:
    """
    完整索引构建流程
    
    Args:
        conn: 数据库连接
        help_dir: MATLAB help 目录路径
        max_workers: 最大线程数 (默认 1)
        
    Returns:
        插入的记录数
    """
    from mdi.cache import batch_insert_paths, rebuild_index
    
    logger.info("开始构建索引...")
    
    # 1. 扫描目录
    func_paths = scan_help_dir(help_dir, max_workers)
    
    if not func_paths:
        logger.warning("未发现任何函数,索引构建失败")
        return 0
    
    # 2. 清空旧索引
    rebuild_index(conn)
    
    # 3. 批量插入
    count = batch_insert_paths(conn, func_paths)
    
    logger.info(f"索引构建完成,共插入 {count} 条记录")
    return count


def update_index(conn, help_dir: Path, max_workers: int = 1) -> Tuple[int, int]:
    """
    增量更新索引 (保留已有缓存)
    
    Args:
        conn: 数据库连接
        help_dir: MATLAB help 目录路径
        max_workers: 最大线程数 (默认 1)
        
    Returns:
        (新增数量, 删除数量)
    """
    import sqlite3
    
    logger.info("开始增量更新索引...")
    
    # 1. 扫描当前目录
    func_paths = scan_help_dir(help_dir, max_workers)
    
    if not func_paths:
        logger.warning("未发现任何函数,更新失败")
        return (0, 0)
    
    # 2. 获取现有索引
    cursor = conn.execute("SELECT name, path FROM docs")
    existing = {row["name"]: row["path"] for row in cursor}
    
    # 3. 计算差异
    new_funcs = set(func_paths.keys()) - set(existing.keys())
    removed_funcs = set(existing.keys()) - set(func_paths.keys())
    updated_funcs = {
        name for name in set(func_paths.keys()) & set(existing.keys())
        if func_paths[name] != existing[name]
    }
    
    # 4. 插入新函数
    new_paths = {name: func_paths[name] for name in new_funcs}
    if new_paths:
        from mdi.cache import batch_insert_paths
        batch_insert_paths(conn, new_paths)
    
    # 5. 更新路径变化的函数
    for name in updated_funcs:
        conn.execute(
            "UPDATE docs SET path = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
            (func_paths[name], name)
        )
    
    # 6. 删除已不存在的函数
    if removed_funcs:
        conn.executemany(
            "DELETE FROM docs WHERE name = ?",
            [(name,) for name in removed_funcs]
        )
    
    conn.commit()
    
    logger.info(
        f"增量更新完成: 新增 {len(new_funcs)}, "
        f"更新 {len(updated_funcs)}, 删除 {len(removed_funcs)}"
    )
    
    return (len(new_funcs) + len(updated_funcs), len(removed_funcs))
