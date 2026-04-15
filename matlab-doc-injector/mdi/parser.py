"""
MarkItDown 解析与降噪模块 - HTML 到 Markdown 的语义化转换
实现正则降噪规则,保留对 LLM 极具价值的代码块、参数表格与数学公式
"""

import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def parse_html_to_md(html_path: Path) -> str:
    """
    将 HTML 文档转换为 Markdown 格式
    
    Args:
        html_path: HTML 文件路径
        
    Returns:
        Markdown 字符串
        
    Raises:
        FileNotFoundError: HTML 文件不存在
        Exception: 解析失败
    """
    try:
        from markitdown import MarkItDown
        
        md_converter = MarkItDown()
        result = md_converter.convert(str(html_path))
        
        if result is None:
            raise ValueError("MarkItDown 返回空结果")
        
        raw_md = result.text_content
        
        if not raw_md or len(raw_md.strip()) == 0:
            logger.warning(f"HTML 文件解析后为空: {html_path}")
            return ""
        
        logger.debug(f"成功解析 HTML: {html_path.name} ({len(raw_md)} 字符)")
        return raw_md
        
    except ImportError:
        logger.error("markitdown 库未安装,请运行: pip install markitdown")
        raise
    except FileNotFoundError:
        logger.error(f"HTML 文件不存在: {html_path}")
        raise
    except Exception as e:
        logger.error(f"HTML 解析失败 [{html_path}]: {e}")
        raise


def denoise_markdown(raw_md: str) -> str:
    """
    对 Markdown 内容进行降噪处理
    
    降噪规则:
    - 移除导航栏元素 (## Navigation, ## See Also 等冗余链接)
    - 清理空行和多余换行
    - 移除版本号/版权信息
    - 保留代码块、参数表格、数学公式
    
    Args:
        raw_md: 原始 Markdown 字符串
        
    Returns:
        降噪后的 Markdown 字符串
    """
    if not raw_md:
        return ""
    
    cleaned = raw_md
    
    # 1. 移除 "See Also" 区块 (通常是链接列表,对 LLM 价值较低)
    cleaned = re.sub(
        r'## See Also\n.*?(?=\n##|\Z)',
        '',
        cleaned,
        flags=re.DOTALL
    )
    
    # 2. 移除 "Web View" 或 "PDF Version" 等导航提示
    cleaned = re.sub(
        r'\[.*?(?:Web View|PDF Version|Previous|Next).*?\]',
        '',
        cleaned
    )
    
    # 3. 移除版权和版本信息
    cleaned = re.sub(
        r'©.*?(?:MathWorks|MATLAB).*',
        '',
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r'R\d{4}[ab].*?(?:version|release).*',
        '',
        cleaned,
        flags=re.IGNORECASE
    )
    
    # 4. 移除 "Open Live Script" 等按钮文本
    cleaned = re.sub(
        r'Open Live Script|Open in MATLAB Online',
        '',
        cleaned,
        flags=re.IGNORECASE
    )
    
    # 5. 清理连续空行 (保留最多 2 个换行)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # 6. 移除行首行尾空白
    cleaned = cleaned.strip()
    
    # 7. 如果内容为空,返回原始内容 (避免过度清理)
    if not cleaned:
        logger.warning("降噪后内容为空,返回原始内容")
        return raw_md.strip()
    
    logger.debug(f"降噪完成: {len(raw_md)} -> {len(cleaned)} 字符")
    return cleaned


def parse_and_cache(html_path: Path, denoise: bool = True) -> str:
    """
    解析 HTML 并可选地进行降噪处理
    
    Args:
        html_path: HTML 文件路径
        denoise: 是否进行降噪处理 (默认 True)
        
    Returns:
        Markdown 字符串
    """
    try:
        raw_md = parse_html_to_md(html_path)
        
        if denoise:
            return denoise_markdown(raw_md)
        else:
            return raw_md.strip()
            
    except Exception as e:
        logger.error(f"解析失败 [{html_path}]: {e}")
        return f"[ERROR] 无法解析文档: {html_path}\n错误信息: {str(e)}"


def extract_sections(md_content: str) -> dict:
    """
    提取 Markdown 中的关键章节 (可选功能)
    
    Args:
        md_content: Markdown 内容
        
    Returns:
        {章节名: 内容} 字典
    """
    sections = {}
    
    # 按二级标题分割
    pattern = r'^## (.+?)$\n(.*?)(?=^## |\Z)'
    matches = re.findall(pattern, md_content, re.MULTILINE | re.DOTALL)
    
    for title, content in matches:
        sections[title.strip()] = content.strip()
    
    return sections


def validate_md_content(md_content: str) -> bool:
    """
    验证 Markdown 内容质量
    
    Args:
        md_content: Markdown 内容
        
    Returns:
        内容是否有效
    """
    if not md_content or len(md_content.strip()) < 50:
        return False
    
    # 检查是否包含基本结构 (至少有一个标题或代码块)
    if not (
        re.search(r'^#+ ', md_content, re.MULTILINE) or
        re.search(r'```', md_content) or
        re.search(r'\|.*\|', md_content)  # 表格
    ):
        return False
    
    return True
