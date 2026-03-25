"""
基础素材模型模块

本模块定义了所有模板共用的基础素材模型和通用响应模型。
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class VideoMaterial(BaseModel):
    """视频素材信息"""
    url: HttpUrl = Field(..., description="视频素材URL")
    material_name: Optional[str] = Field(None, description="素材名称，不传则使用默认名称")
    start_time: Optional[float] = Field(0, ge=0, description="开始时间（秒），默认从0开始")
    duration: Optional[float] = Field(None, ge=0, description="持续时长（秒），不传则使用视频完整时长")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com/video.mp4",
                "material_name": "主视频",
                "start_time": 0,
                "duration": 10.5
            }
        }
    }


class AudioMaterial(BaseModel):
    """音频素材信息"""
    url: HttpUrl = Field(..., description="音频素材URL")
    material_name: Optional[str] = Field(None, description="素材名称")
    volume: float = Field(1.0, ge=0, le=2.0, description="音量倍数，0-2之间，默认1.0")
    fade_in: Optional[float] = Field(None, ge=0, description="淡入时长（秒）")
    fade_out: Optional[float] = Field(None, ge=0, description="淡出时长（秒）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com/audio.mp3",
                "material_name": "背景音乐",
                "volume": 0.8,
                "fade_in": 1.0,
                "fade_out": 2.0
            }
        }
    }


class ImageMaterial(BaseModel):
    """图片素材信息"""
    url: HttpUrl = Field(..., description="图片素材URL")
    material_name: Optional[str] = Field(None, description="素材名称")
    duration: float = Field(..., gt=0, le=300, description="显示时长（秒），最大300秒")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com/image.jpg",
                "material_name": "封面图",
                "duration": 5.0
            }
        }
    }


class TextMaterial(BaseModel):
    """文本素材信息"""
    content: str = Field(..., min_length=1, max_length=500, description="文本内容")
    font_size: int = Field(30, ge=12, le=200, description="字体大小，默认30")
    color: str = Field("#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$", description="字体颜色，十六进制格式")
    position_x: float = Field(0.5, ge=0, le=1, description="水平位置（0-1之间，0.5为居中）")
    position_y: float = Field(0.5, ge=0, le=1, description="垂直位置（0-1之间，0.5为居中）")
    start_time: float = Field(0, ge=0, description="开始时间（秒）")
    duration: float = Field(..., gt=0, le=300, description="持续时长（秒）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "欢迎使用剪映自动化",
                "font_size": 40,
                "color": "#FFFFFF",
                "position_x": 0.5,
                "position_y": 0.2,
                "start_time": 0,
                "duration": 5.0
            }
        }
    }


class StickerMaterial(BaseModel):
    """贴纸信息"""
    sticker_id: str = Field(..., min_length=1, description="贴纸ID或资源标识")
    position_x: float = Field(0.5, ge=0, le=1, description="水平位置")
    position_y: float = Field(0.5, ge=0, le=1, description="垂直位置")
    scale: float = Field(1.0, ge=0.1, le=5.0, description="缩放比例")
    start_time: float = Field(0, ge=0, description="开始时间（秒）")
    duration: float = Field(..., gt=0, le=300, description="持续时长（秒）")


class CreateDraftResponse(BaseModel):
    """创建草稿响应"""
    code: int = Field(0, description="状态码，0表示成功")
    message: str = Field("success", description="状态信息")
    draft_url: str = Field(..., description="草稿下载URL")
    draft_id: str = Field(..., description="草稿ID")
    tip_url: str = Field(..., description="帮助文档URL")
    template_id: str = Field(..., description="使用的模板ID")
    estimated_duration: Optional[float] = Field(None, description="预估视频时长（秒）")


class TemplateInfo(BaseModel):
    """模板信息响应"""
    template_id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    supported_features: List[str] = Field(..., description="支持的功能列表")
    max_videos: Optional[int] = Field(None, description="最大视频数量")
    max_images: Optional[int] = Field(None, description="最大图片数量")
    max_audios: Optional[int] = Field(None, description="最大音频数量")
    max_texts: Optional[int] = Field(None, description="最大文字数量")
