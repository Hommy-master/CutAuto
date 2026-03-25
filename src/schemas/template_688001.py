"""
模板 688001 请求参数模块

该模板适用于：多视频混剪 + 背景音乐 + 标题文字
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

from src.schemas.template_base import VideoMaterial, AudioMaterial, TextMaterial


class CreateDraftRequest688001(BaseModel):
    """
    模板 688001 请求参数
    
    该模板适用于：多视频混剪 + 背景音乐 + 标题文字
    支持替换主视频、背景音乐和标题文字
    """
    template_id: Literal["688001"] = Field("688001", description="模板ID，固定为688001")
    
    # 视频素材列表（至少1个，最多10个）
    videos: List[VideoMaterial] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="视频素材列表，至少1个，最多10个"
    )
    
    # 背景音乐（可选）
    audio: Optional[AudioMaterial] = Field(
        None,
        description="背景音乐素材，不传则使用模板默认音乐"
    )
    
    # 标题文字（可选）
    title: Optional[TextMaterial] = Field(
        None,
        description="标题文字，不传则使用模板默认标题"
    )
    
    # 转场效果
    transition_type: Optional[str] = Field(
        "fade",
        description="转场效果类型：fade（淡入淡出）、slide（滑动）、zoom（缩放）"
    )
    
    # 输出配置
    output_duration: Optional[float] = Field(
        None,
        gt=0,
        le=600,
        description="输出视频总时长（秒），不传则自动计算"
    )
    
    @field_validator('transition_type')
    def validate_transition_type(cls, v):
        """校验转场类型是否合法"""
        allowed_transitions = ['fade', 'slide', 'zoom', 'none']
        if v and v not in allowed_transitions:
            raise ValueError(f"转场类型必须是以下之一：{', '.join(allowed_transitions)}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "688001",
                "videos": [
                    {
                        "url": "https://example.com/video1.mp4",
                        "material_name": "视频1",
                        "duration": 10
                    },
                    {
                        "url": "https://example.com/video2.mp4",
                        "material_name": "视频2",
                        "duration": 8
                    }
                ],
                "audio": {
                    "url": "https://example.com/music.mp3",
                    "volume": 0.6
                },
                "title": {
                    "content": "精彩视频混剪",
                    "font_size": 50,
                    "color": "#FFD700",
                    "position_y": 0.1
                },
                "transition_type": "fade"
            }
        }
    }
