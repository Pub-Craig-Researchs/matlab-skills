"""
CLI 命令行入口 - 参数解析与主工作流调度
支持查询函数文档、索引管理、配置选项等功能
"""

import sys
import argparse
import logging
import io
from pathlib import Path
from typing import Optional

# 修复 Windows 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from mdi.config import MDIConfig
from mdi.cache import (
    get_connection, init_db, lookup_function, 
    cache_content, get_stats
)
from mdi.indexer import bootstrap_index, update_index
from mdi.parser import parse_and_cache

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """
    配置日志输出
    
    Args:
        verbose: 是否启用详细日志
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog='mdi',
        description='MATLAB Doc Injector (MDI) v2.0 - 零延迟本地文档注入引擎',
        epilog='示例:\n'
               '  mdi fmincon                  查询 fmincon 文档\n'
               '  mdi fmincon -o output/       输出到文件\n'
               '  mdi --init                   重建索引\n'
               '  mdi --stats                  显示缓存统计\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 查询参数
    parser.add_argument(
        'function',
        nargs='?',
        help='MATLAB 函数名称 (如 fmincon, plot 等)'
    )
    
    # 输出选项
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='输出目录路径 (默认当前目录下的 mdi-output/)'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='输出未降噪的原始 Markdown'
    )
    
    # 索引管理
    index_group = parser.add_mutually_exclusive_group()
    index_group.add_argument(
        '--init',
        action='store_true',
        help='强制重建索引'
    )
    index_group.add_argument(
        '--update',
        action='store_true',
        help='增量更新索引'
    )
    index_group.add_argument(
        '--stats',
        action='store_true',
        help='显示缓存统计信息'
    )
    
    # 配置选项
    parser.add_argument(
        '--matlab-path',
        type=Path,
        help='手动指定 MATLAB 根目录路径'
    )
    parser.add_argument(
        '--db-path',
        type=Path,
        help='SQLite 数据库路径 (默认 ~/.mdi/cache.db)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='索引构建的并发线程数 (默认 1,使用 0 表示自动检测 CPU 核心数)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='启用详细日志输出'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser


def cmd_query(args: argparse.Namespace, config: MDIConfig) -> int:
    """
    查询函数文档命令
    
    Args:
        args: 命令行参数
        config: 配置实例
        
    Returns:
        退出码 (0=成功, 1=失败)
    """
    func_name = args.function.lower()
    
    logger.info(f"查询函数文档: {func_name}")
    
    with get_connection(config.db_path) as conn:
        # 1. 查询缓存
        result = lookup_function(conn, func_name)
        
        if result is None:
            print(f"[ERROR] 未找到函数 '{func_name}' 的文档", file=sys.stderr)
            print("提示: 运行 'mdi --update' 更新索引", file=sys.stderr)
            return 1
        
        content, html_path = result
        
        # 2. 缓存命中
        if content:
            logger.info(f"缓存命中: {func_name}")
            md_content = content
        else:
            # 3. 缓存未命中,解析 HTML
            logger.info(f"缓存未命中,开始解析: {html_path}")
            md_content = parse_and_cache(
                Path(html_path), 
                denoise=not args.raw
            )
            
            # 4. 回写缓存
            if not args.raw and md_content and not md_content.startswith("[ERROR]"):
                cache_content(conn, func_name, md_content)
                logger.info(f"缓存已更新: {func_name}")
    
    # 5. 输出结果
    if args.output:
        # 输出到文件
        output_file = args.output / f"{func_name}.md"
        args.output.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md_content, encoding='utf-8')
        print(f"[OK] 文档已保存: {output_file}")
    else:
        # 输出到终端
        print("\n" + "="*80)
        print(f"MATLAB Function: {func_name}")
        print("="*80 + "\n")
        print(md_content)
        print("\n" + "="*80)
    
    return 0


def cmd_init(args: argparse.Namespace, config: MDIConfig) -> int:
    """
    重建索引命令
    
    Args:
        args: 命令行参数
        config: 配置实例
        
    Returns:
        退出码
    """
    logger.info("执行索引重建...")
    
    # 处理 workers 参数: 0 表示自动检测
    max_workers = args.workers if args.workers > 0 else None
    
    with get_connection(config.db_path) as conn:
        count = bootstrap_index(conn, config.help_dir, max_workers)
    
    if count > 0:
        print(f"[OK] 索引重建完成,共 {count} 个函数")
        return 0
    else:
        print("[ERROR] 索引重建失败", file=sys.stderr)
        return 1


def cmd_update(args: argparse.Namespace, config: MDIConfig) -> int:
    """
    增量更新索引命令
    
    Args:
        args: 命令行参数
        config: 配置实例
        
    Returns:
        退出码
    """
    logger.info("执行增量更新...")
    
    # 处理 workers 参数: 0 表示自动检测
    max_workers = args.workers if args.workers > 0 else None
    
    with get_connection(config.db_path) as conn:
        added, removed = update_index(conn, config.help_dir, max_workers)
    
    print(f"[OK] 增量更新完成: 新增 {added} 个, 删除 {removed} 个")
    return 0


def cmd_stats(args: argparse.Namespace, config: MDIConfig) -> int:
    """
    显示缓存统计命令
    
    Args:
        args: 命令行参数
        config: 配置实例
        
    Returns:
        退出码
    """
    with get_connection(config.db_path) as conn:
        stats = get_stats(conn)
    
    print("\n" + "="*60)
    print("MDI Cache Statistics")
    print("="*60)
    print(f"Total Functions:    {stats['total']}")
    print(f"Cached (Parsed):    {stats['cached']}")
    print(f"Uncached:           {stats['uncached']}")
    print(f"Cache Hit Rate:     {stats['cache_hit_rate']}")
    print(f"Database Size:      {stats['db_size_mb']}")
    print("="*60 + "\n")
    
    return 0


def main():
    """
    MDI 主入口函数
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # 配置日志
    setup_logging(args.verbose)
    
    try:
        # 1. 加载配置
        config = MDIConfig.create(
            matlab_path=args.matlab_path,
            db_path=args.db_path,
            output_dir=args.output
        )
        
        # 2. 初始化数据库
        init_db(config.db_path)
        
        # 3. 检查索引是否存在
        with get_connection(config.db_path) as conn:
            stats = get_stats(conn)
            has_index = stats['total'] > 0
        
        # 4. 自动构建索引 (如果不存在且不是管理命令)
        if not has_index and not args.init and not args.update and not args.stats:
            logger.info("索引不存在,自动构建...")
            # 处理 workers 参数: 0 表示自动检测
            max_workers = args.workers if args.workers > 0 else None
            with get_connection(config.db_path) as conn:
                bootstrap_index(conn, config.help_dir, max_workers)
        
        # 5. 执行命令
        if args.function:
            # 查询文档
            return cmd_query(args, config)
        elif args.init:
            # 重建索引
            return cmd_init(args, config)
        elif args.update:
            # 增量更新
            return cmd_update(args, config)
        elif args.stats:
            # 显示统计
            return cmd_stats(args, config)
        else:
            # 无操作,显示帮助
            parser.print_help()
            return 0
            
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[INFO] 操作已取消")
        return 130
    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        print(f"[ERROR] 程序执行失败: {e}", file=sys.stderr)
        if not args.verbose:
            print("提示: 使用 -v 参数查看详细错误信息", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
