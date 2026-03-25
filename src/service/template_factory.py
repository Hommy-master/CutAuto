"""
处理器工厂模块

本模块实现了处理器工厂模式，用于动态创建和管理模板处理器。
"""

from typing import Any, Dict, List, Optional

from src.service.template_base import BaseProcessor
from src.service.template_processor_688001 import Processor688001
from src.service.template_processor_688002 import Processor688002
from src.service.template_processor_688003 import Processor688003
from src.schemas.template_registry import get_template_request
from src.utils.logger import logger
from exceptions import CustomException, CustomError as ErrorCode


class ProcessorFactory:
    """
    处理器工厂类
    
    使用工厂模式管理所有模板处理器，支持动态注册和获取处理器。
    """
    
    # 处理器注册表：模板ID -> 处理器类
    _processors: Dict[str, type] = {}
    
    @classmethod
    def register(cls, template_id: str, processor_class: type) -> None:
        """
        注册处理器
        
        Args:
            template_id: 模板ID
            processor_class: 处理器类
        """
        cls._processors[template_id] = processor_class
        logger.info(f"处理器已注册: {template_id} -> {processor_class.__name__}")
    
    @classmethod
    def get(cls, template_id: str) -> Optional[BaseProcessor]:
        """
        获取处理器实例
        
        Args:
            template_id: 模板ID
            
        Returns:
            处理器实例，如果未找到则返回None
        """
        processor_class = cls._processors.get(template_id)
        if processor_class:
            return processor_class()
        return None
    
    @classmethod
    def exists(cls, template_id: str) -> bool:
        """
        检查模板是否已注册
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否已注册
        """
        return template_id in cls._processors
    
    @classmethod
    def list(cls) -> List[str]:
        """
        获取所有已注册的模板ID列表
        
        Returns:
            模板ID列表
        """
        return list(cls._processors.keys())


# 注册所有处理器
ProcessorFactory.register("688001", Processor688001)
ProcessorFactory.register("688002", Processor688002)
ProcessorFactory.register("688003", Processor688003)


# ==================== 服务层函数 ====================

def create_draft(template_id: str, params: Any) -> Dict[str, Any]:
    """
    使用指定模板创建草稿
    
    Args:
        template_id: 模板ID
        params: 模板参数（已验证）
        
    Returns:
        草稿创建结果
        
    Raises:
        CustomException: 创建失败
    """
    processor = ProcessorFactory.get(template_id)
    
    if not processor:
        raise CustomException(
            ErrorCode.TEMPLATE_NOT_FOUND,
            detail=f"不支持的模板ID: {template_id}"
        )
    
    logger.info(f"开始创建草稿: template_id={template_id}")
    return processor.process(params)


def list_all() -> List[Dict[str, Any]]:
    """
    获取所有可用模板列表
    
    Returns:
        模板信息列表
    """
    from src.schemas.template import list_templates
    return list_templates()


def validate_params(template_id: str, params: Dict[str, Any]) -> Any:
    """
    验证模板参数
    
    Args:
        template_id: 模板ID
        params: 原始参数字典
        
    Returns:
        验证后的参数对象
        
    Raises:
        CustomException: 参数验证失败
    """
    # 获取对应的请求Schema类
    request_class = get_template_request(template_id)
    
    if not request_class:
        raise CustomException(
            ErrorCode.TEMPLATE_NOT_FOUND,
            detail=f"不支持的模板ID: {template_id}"
        )
    
    try:
        # 使用Pydantic验证参数
        validated = request_class(**params)
        logger.info(f"参数验证通过: {template_id}")
        return validated
    except Exception as e:
        logger.error(f"参数验证失败: {e}")
        raise CustomException(
            ErrorCode.PARAMETER_ERROR,
            detail=f"参数验证失败: {str(e)}"
        )
