"""
模板 688002 请求参数模块

该模板适用于：图片轮播 + 背景音乐 + 动态文字
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

from src.schemas.template_base import ImageMaterial, AudioMaterial, TextMaterial


class CreateDraftRequest688002(BaseModel):
    """
    模板 688002 请求参数
    
    该模板适用于：图片轮播 + 背景音乐 + 动态文字
    支持替换图片、背景音乐和动态文字
    """
    template_id: Literal["688002"] = Field("688002", description="模板ID，固定为688002")
    
    # 图片素材列表（至少2张，最多20张）
    images: List[ImageMaterial] = Field(
        ...,
        min_items=2,
        max_items=20,
        description="图片素材列表，至少2张，最多20张"
    )
    
    # 背景音乐（可选）
    audio: Optional[AudioMaterial] = Field(
        None,
        description="背景音乐素材"
    )
    
    # 动态文字列表
    texts: Optional[List[TextMaterial]] = Field(
        None,
        max_items=5,
        description="动态文字列表，最多5个"
    )
    
    # 动画效果
    animation_type: str = Field(
        "ken_burns",
        description="图片动画类型：ken_burns（肯伯恩斯）、slide（滑动）、fade（淡入淡出）"
    )
    
    # 每张图片显示时长
    image_display_duration: float = Field(
        5.0,
        ge=1,
        le=30,
        description="每张图片显示时长（秒），默认5秒"
    )
    
    @field_validator('animation_type')
    def validate_animation_type(cls, v):
        """校验动画类型是否合法"""
        allowed_animations = ['ken_burns', 'slide', 'fade', 'zoom', 'none']
        if v not in allowed_animations:
            raise ValueError(f"动画类型必须是以下之一：{', '.join(allowed_animations)}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "688002",
                "images": [
                    {
                        "url": "https://example.com/photo1.jpg",
                        "duration": 5
                    },
                    {
                        "url": "https://example.com/photo2.jpg",
                        "duration": 5
                    },
                    {
                        "url": "https://example.com/photo3.jpg",
                        "duration": 5
                    }
                ],
                "audio": {
                    "url": "https://example.com/background.mp3",
                    "volume": 0.7
                },
                "texts": [
                    {
                        "content": "美好回忆",
                        "font_size": 45,
                        "color": "#FFFFFF",
                        "start_time": 0,
                        "duration": 5
                    }
                ],
                "animation_type": "ken_burns",
                "image_display_duration": 5
            }
        }
    }
