"""
配置管理模块 - MATLAB 路径检测与配置
实现混合模式路径检测: 自动检测 -> 常见路径扫描 -> 手动指定
"""

import os
import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class MDIConfig:
    """MDI 配置数据类"""
    matlab_root: Path
    help_dir: Path
    db_path: Path
    output_dir: Path
    
    @classmethod
    def create(
        cls,
        matlab_path: Optional[Path] = None,
        db_path: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ) -> "MDIConfig":
        """
        创建配置实例
        
        Args:
            matlab_path: MATLAB 根目录路径 (可选,自动检测)
            db_path: SQLite 数据库路径 (可选,默认 ~/.mdi/cache.db)
            output_dir: Markdown 输出目录 (可选,默认 ./mdi-output/)
            
        Returns:
            MDIConfig 实例
        """
        # 检测 MATLAB 路径
        if matlab_path:
            if not matlab_path.exists():
                raise FileNotFoundError(f"MATLAB 路径不存在: {matlab_path}")
            matlab_root = matlab_path
        else:
            matlab_root = detect_matlab_root()
        
        help_dir = matlab_root / "help"
        if not help_dir.exists():
            raise FileNotFoundError(f"MATLAB help 目录不存在: {help_dir}")
        
        # 默认数据库路径
        if db_path is None:
            db_path = Path.home() / ".mdi" / "cache.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 默认输出目录
        if output_dir is None:
            output_dir = Path.cwd() / "mdi-output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return cls(
            matlab_root=matlab_root,
            help_dir=help_dir,
            db_path=db_path,
            output_dir=output_dir
        )


def detect_matlab_root() -> Path:
    """
    混合模式检测 MATLAB 根目录
    
    优先级:
    1. matlabroot 命令
    2. Windows 注册表
    3. 常见安装路径扫描
    4. 环境变量 MATLAB_ROOT
    
    Returns:
        MATLAB 根目录路径
        
    Raises:
        FileNotFoundError: 无法找到 MATLAB 安装
    """
    # 1. 尝试 MATLAB CLI docroot 命令 (最准确)
    doc_root = _detect_via_matlab_cli()
    if doc_root:
        logger.info(f"通过 MATLAB docroot 命令检测到: {doc_root}")
        # docroot 返回的就是 help 目录
        if doc_root.name.lower() == "help":
            return doc_root.parent
        else:
            return doc_root
    
    # 2. 尝试 matlabroot 命令
    matlab_root = _detect_via_matlabroot()
    if matlab_root:
        logger.info(f"通过 matlabroot 命令检测到: {matlab_root}")
        return matlab_root
    
    # 3. Windows 注册表检测
    if os.name == "nt":
        matlab_root = _detect_via_registry()
        if matlab_root:
            logger.info(f"通过 Windows 注册表检测到: {matlab_root}")
            return matlab_root
    
    # 4. 常见安装路径扫描
    matlab_root = _detect_common_paths()
    if matlab_root:
        logger.info(f"通过常见路径扫描检测到: {matlab_root}")
        return matlab_root
    
    # 5. 环境变量
    env_path = os.environ.get("MATLAB_ROOT")
    if env_path:
        matlab_root = Path(env_path)
        if matlab_root.exists() and (matlab_root / "help").exists():
            logger.info(f"通过环境变量 MATLAB_ROOT 检测到: {matlab_root}")
            return matlab_root
    
    raise FileNotFoundError(
        "无法自动检测 MATLAB 安装路径。\n"
        "请通过以下方式之一指定:\n"
        "  1. 命令行参数: mdi --matlab-path /path/to/matlab\n"
        "  2. 环境变量: 设置 MATLAB_ROOT=/path/to/matlab\n"
        "  3. 确保 MATLAB 已正确安装并添加到系统 PATH"
    )


def _detect_via_matlab_cli() -> Optional[Path]:
    """通过 MATLAB CLI docroot 命令检测文档路径"""
    try:
        # 使用 matlab -batch 执行 docroot 命令
        result = subprocess.run(
            ["matlab", "-batch", "disp(docroot); exit;"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # 提取输出中的路径 (最后一行有效输出)
            lines = result.stdout.strip().split("\n")
            # 过滤掉 MATLAB 启动信息,找包含路径的行
            for line in reversed(lines):
                line = line.strip()
                # 匹配包含 help 或 doc 的路径
                if any(keyword in line.lower() for keyword in ["help", "doc"]) and \
                   ("matlab" in line.lower() or line.startswith("C:\\") or line.startswith("D:\\")):
                    doc_path = Path(line)
                    if doc_path.exists():
                        return doc_path
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"MATLAB CLI docroot 检测失败: {e}")
    
    return None


def _detect_via_matlabroot() -> Optional[Path]:
    """通过 matlabroot 命令检测 MATLAB 路径"""
    try:
        result = subprocess.run(
            ["matlab", "-batch", "disp(matlabroot); exit;"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            # 提取最后一行 (matlabroot 输出)
            matlab_root = Path(output.split("\n")[-1].strip())
            if matlab_root.exists() and (matlab_root / "help").exists():
                return matlab_root
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"matlabroot 命令检测失败: {e}")
    
    return None


def _detect_via_registry() -> Optional[Path]:
    """通过 Windows 注册表检测 MATLAB 路径"""
    try:
        import winreg
        
        # 尝试常见的 MATLAB 注册表键
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\MathWorks\MATLAB"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\MathWorks\MATLAB"),
        ]
        
        for hkey, reg_path in registry_paths:
            try:
                with winreg.OpenKey(hkey, reg_path) as key:
                    # 查找最新的 MATLAB 版本
                    max_version = ""
                    matlab_path = None
                    
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if subkey_name.startswith("R"):
                                if subkey_name > max_version:
                                    max_version = subkey_name
                                    subkey_path = f"{reg_path}\\{subkey_name}"
                                    with winreg.OpenKey(hkey, subkey_path) as subkey:
                                        matlab_path, _ = winreg.QueryValueEx(subkey, "MATLABROOT")
                            i += 1
                        except OSError:
                            break
                    
                    if matlab_path:
                        path = Path(matlab_path)
                        if path.exists() and (path / "help").exists():
                            return path
            except (OSError, FileNotFoundError):
                continue
    except ImportError:
        logger.debug("winreg 模块不可用")
    
    return None


def _detect_common_paths() -> Optional[Path]:
    """扫描常见 MATLAB 安装路径"""
    common_paths = []
    
    if os.name == "nt":  # Windows
        base_paths = [
            Path("C:/Program Files/MATLAB"),
            Path("D:/Program Files/MATLAB"),
            Path("C:/Program Files (x86)/MATLAB"),
        ]
        for base in base_paths:
            if base.exists():
                # 查找最新的 R 版本
                versions = sorted([
                    d for d in base.iterdir()
                    if d.is_dir() and d.name.startswith("R")
                ], reverse=True)
                if versions:
                    common_paths.append(versions[0])
    else:  # Linux/macOS
        base_paths = [
            Path("/usr/local/MATLAB"),
            Path("/opt/MATLAB"),
            Path.home() / "MATLAB",
        ]
        for base in base_paths:
            if base.exists():
                versions = sorted([
                    d for d in base.iterdir()
                    if d.is_dir() and d.name.startswith("R")
                ], reverse=True)
                if versions:
                    common_paths.append(versions[0])
    
    # 验证路径
    for path in common_paths:
        if (path / "help").exists():
            return path
    
    return None
