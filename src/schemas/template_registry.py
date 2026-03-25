"""
模板注册表模块

本模块管理所有模板的注册和查询功能。
"""

from typing import List, Dict, Any, Optional

# 模板ID到请求Schema类的映射，用于动态路由处理
TEMPLATE_REGISTRY = {}


def register_template(template_id: str, request_class: type) -> None:
    """
    注册模板请求类
    
    Args:
        template_id: 模板ID
        request_class: 模板请求参数类
    """
    TEMPLATE_REGISTRY[template_id] = request_class


def get_template_request(template_id: str) -> Optional[type]:
    """
    根据模板ID获取对应的请求参数类
    
    Args:
        template_id: 模板ID字符串
        
    Returns:
        对应的Schema类，如果未找到则返回None
    """
    return TEMPLATE_REGISTRY.get(template_id)


def list_templates() -> List[Dict[str, Any]]:
    """
    获取所有可用模板列表
    
    Returns:
        模板信息列表
    """
    templates = [
        {
            "template_id": "688001",
            "name": "图片轮播模板",
            "description": "3张图片轮播 + 背景音乐",
            "supported_features": ["image", "audio"]
        },
        {
            "template_id": "688002",
            "name": "图片轮播模板",
            "description": "图片轮播 + 背景音乐 + 动态文字",
            "supported_features": ["image", "audio", "text", "animation"]
        },
        {
            "template_id": "688003",
            "name": "视频特效模板",
            "description": "单视频 + 特效 + 贴纸 + 字幕",
            "supported_features": ["video", "subtitle", "sticker", "effect"]
        }
    ]
    return templates


# ==================== 注册所有模板请求类 ====================
# 延迟导入避免循环依赖，在模块加载时注册

def _register_all_templates():
    """注册所有模板请求类到注册表"""
    try:
        from .template_688001 import CreateDraftRequest688001
        from .template_688002 import CreateDraftRequest688002
        from .template_688003 import CreateDraftRequest688003
        
        register_template("688001", CreateDraftRequest688001)
        register_template("688002", CreateDraftRequest688002)
        register_template("688003", CreateDraftRequest688003)
    except ImportError:
        # 测试时可能模块未完全加载
        pass


# 模块加载时自动注册
_register_all_templates()
