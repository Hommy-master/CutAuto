"""
基础处理器模块

本模块定义了模板处理器的抽象基类和通用工具函数。
"""

import os
import shutil
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import config
from src.utils.logger import logger
from src.utils.download import download
from exceptions import CustomException, CustomError as ErrorCode


class BaseProcessor(ABC):
    """
    模板处理器抽象基类
    
    所有具体模板处理器必须继承此类并实现process方法。
    提供通用的草稿创建流程和工具方法。
    """
    
    def __init__(self, template_id: str):
        """
        初始化处理器
        
        Args:
            template_id: 模板ID
        """
        self.template_id = template_id
        self.template_path = os.path.join(config.TEMPLATE_DIR, template_id)
        self.draft_id = self._generate_draft_id()
        self.draft_path = os.path.join(config.DRAFT_DIR, self.draft_id)
        self.temp_files: List[str] = []  # 临时文件列表，用于清理
    
    def _generate_draft_id(self) -> str:
        """
        生成唯一草稿ID
        
        Returns:
            草稿ID字符串
        """
        return f"{self.template_id}_{uuid.uuid4().hex[:8]}"
    
    @abstractmethod
    def process(self, params: Any) -> Dict[str, Any]:
        """
        处理模板创建请求（子类必须实现）
        
        Args:
            params: 模板参数
            
        Returns:
            处理结果字典
        """
        pass
    
    def _copy_template(self) -> None:
        """
        复制模板文件到草稿目录
        
        Raises:
            CustomException: 模板复制失败
        """
        try:
            if os.path.exists(self.template_path):
                shutil.copytree(self.template_path, self.draft_path)
                logger.info(f"模板复制成功: {self.template_path} -> {self.draft_path}")
            else:
                # 如果模板目录不存在，创建空目录
                os.makedirs(self.draft_path, exist_ok=True)
                logger.warning(f"模板目录不存在，创建空目录: {self.draft_path}")
        except Exception as e:
            logger.error(f"模板复制失败: {e}")
            raise CustomException(
                ErrorCode.TEMPLATE_COPY_ERROR,
                detail=f"无法复制模板 {self.template_id}"
            )
    
    def _download_material(self, url: str, filename: Optional[str] = None) -> str:
        """
        下载素材文件
        
        Args:
            url: 素材URL
            filename: 可选的文件名
            
        Returns:
            下载后的本地文件路径
            
        Raises:
            CustomException: 下载失败
        """
        try:
            local_path = download(url, config.TEMP_DIR)
            self.temp_files.append(local_path)
            logger.info(f"素材下载成功: {url} -> {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"素材下载失败: {url}, 错误: {e}")
            raise CustomException(
                ErrorCode.MATERIAL_DOWNLOAD_ERROR,
                detail=f"无法下载素材: {url}"
            )
    
    def _calculate_duration(self, materials: List[Dict[str, Any]]) -> float:
        """
        计算素材总时长
        
        Args:
            materials: 素材列表，每个素材包含duration字段
            
        Returns:
            总时长（秒）
        """
        total = 0.0
        for material in materials:
            if isinstance(material, dict) and 'duration' in material:
                total += material.get('duration', 0)
        return total
    
    def _build_response(self, estimated_duration: Optional[float] = None) -> Dict[str, Any]:
        """
        构建标准响应
        
        Args:
            estimated_duration: 预估视频时长
            
        Returns:
            响应字典
        """
        return {
            "draft_id": self.draft_id,
            "draft_url": f"{config.DRAFT_BASE_URL}/{self.draft_id}",
            "tip_url": config.TIP_URL,
            "template_id": self.template_id,
            "estimated_duration": estimated_duration
        }
    
    def cleanup(self) -> None:
        """
        清理临时文件
        
        在草稿创建完成后调用，清理下载的临时素材。
        """
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"临时文件已清理: {temp_file}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {temp_file}, 错误: {e}")
        self.temp_files.clear()
