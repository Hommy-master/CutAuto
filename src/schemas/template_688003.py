"""
模板 688003 请求参数模块

该模板适用于：单视频 + 特效 + 贴纸 + 字幕
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

from src.schemas.template_base import VideoMaterial, TextMaterial, StickerMaterial


class CreateDraftRequest688003(BaseModel):
    """
    模板 688003 请求参数
    
    该模板适用于：单视频 + 特效 + 贴纸 + 字幕
    支持添加特效、贴纸和字幕到主视频
    """
    template_id: Literal["688003"] = Field("688003", description="模板ID，固定为688003")
    
    # 主视频（必须）
    video: VideoMaterial = Field(
        ...,
        description="主视频素材"
    )
    
    # 字幕列表
    subtitles: Optional[List[TextMaterial]] = Field(
        None,
        max_items=20,
        description="字幕列表，最多20条"
    )
    
    # 贴纸列表
    stickers: Optional[List[StickerMaterial]] = Field(
        None,
        max_items=10,
        description="贴纸列表，最多10个"
    )
    
    # 视频特效
    video_effect: Optional[str] = Field(
        None,
        description="视频特效类型：beauty（美颜）、vintage（复古）、cyberpunk（赛博朋克）"
    )
    
    # 滤镜强度
    filter_intensity: float = Field(
        0.5,
        ge=0,
        le=1,
        description="滤镜强度，0-1之间，默认0.5"
    )
    
    # 导出配置
    export_quality: str = Field(
        "1080p",
        description="导出质量：720p、1080p、2k、4k"
    )
    
    @field_validator('video_effect')
    def validate_video_effect(cls, v):
        """校验视频特效类型"""
        if v is None:
            return v
        allowed_effects = ['beauty', 'vintage', 'cyberpunk', 'film', 'none']
        if v not in allowed_effects:
            raise ValueError(f"特效类型必须是以下之一：{', '.join(allowed_effects)}")
        return v
    
    @field_validator('export_quality')
    def validate_export_quality(cls, v):
        """校验导出质量"""
        allowed_qualities = ['720p', '1080p', '2k', '4k']
        if v not in allowed_qualities:
            raise ValueError(f"导出质量必须是以下之一：{', '.join(allowed_qualities)}")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "688003",
                "video": {
                    "url": "https://example.com/main.mp4",
                    "material_name": "主视频"
                },
                "subtitles": [
                    {
                        "content": "第一行字幕",
                        "font_size": 24,
                        "position_y": 0.85,
                        "start_time": 2,
                        "duration": 3
                    }
                ],
                "stickers": [
                    {
                        "sticker_id": "sticker_001",
                        "position_x": 0.8,
                        "position_y": 0.2,
                        "scale": 1.5,
                        "duration": 5
                    }
                ],
                "video_effect": "vintage",
                "filter_intensity": 0.6,
                "export_quality": "1080p"
            }
        }
    }
