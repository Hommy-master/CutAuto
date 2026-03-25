"""
模板参数定义模块

本模块定义了各模板的请求参数，使用 Pydantic 进行严格的参数校验。
支持模板：688001、688002、688003 及后续扩展模板。
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, validator


# ==================== 基础素材模型 ====================

class VideoMaterial(BaseModel):
    """视频素材信息"""
    url: HttpUrl = Field(..., description="视频素材URL")
    material_name: Optional[str] = Field(None, description="素材名称，不传则使用默认名称")
    start_time: Optional[float] = Field(0, ge=0, description="开始时间（秒），默认从0开始")
    duration: Optional[float] = Field(None, ge=0, description="持续时长（秒），不传则使用视频完整时长")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/video.mp4",
                "material_name": "主视频",
                "start_time": 0,
                "duration": 10.5
            }
        }


class AudioMaterial(BaseModel):
    """音频素材信息"""
    url: HttpUrl = Field(..., description="音频素材URL")
    material_name: Optional[str] = Field(None, description="素材名称")
    volume: float = Field(1.0, ge=0, le=2.0, description="音量倍数，0-2之间，默认1.0")
    fade_in: Optional[float] = Field(None, ge=0, description="淡入时长（秒）")
    fade_out: Optional[float] = Field(None, ge=0, description="淡出时长（秒）")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/audio.mp3",
                "material_name": "背景音乐",
                "volume": 0.8,
                "fade_in": 1.0,
                "fade_out": 2.0
            }
        }


class ImageMaterial(BaseModel):
    """图片素材信息"""
    url: HttpUrl = Field(..., description="图片素材URL")
    material_name: Optional[str] = Field(None, description="素材名称")
    duration: float = Field(..., gt=0, le=300, description="显示时长（秒），最大300秒")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/image.jpg",
                "material_name": "封面图",
                "duration": 5.0
            }
        }


class TextMaterial(BaseModel):
    """文本素材信息"""
    content: str = Field(..., min_length=1, max_length=500, description="文本内容")
    font_size: int = Field(30, ge=12, le=200, description="字体大小，默认30")
    color: str = Field("#FFFFFF", regex=r"^#[0-9A-Fa-f]{6}$", description="字体颜色，十六进制格式")
    position_x: float = Field(0.5, ge=0, le=1, description="水平位置（0-1之间，0.5为居中）")
    position_y: float = Field(0.5, ge=0, le=1, description="垂直位置（0-1之间，0.5为居中）")
    start_time: float = Field(0, ge=0, description="开始时间（秒）")
    duration: float = Field(..., gt=0, le=300, description="持续时长（秒）")
    
    class Config:
        schema_extra = {
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


# ==================== 模板 688001 参数 ====================

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
    
    @validator('transition_type')
    def validate_transition_type(cls, v):
        """校验转场类型是否合法"""
        allowed_transitions = ['fade', 'slide', 'zoom', 'none']
        if v and v not in allowed_transitions:
            raise ValueError(f"转场类型必须是以下之一：{', '.join(allowed_transitions)}")
        return v
    
    class Config:
        schema_extra = {
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


# ==================== 模板 688002 参数 ====================

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
    
    @validator('animation_type')
    def validate_animation_type(cls, v):
        """校验动画类型是否合法"""
        allowed_animations = ['ken_burns', 'slide', 'fade', 'zoom', 'none']
        if v not in allowed_animations:
            raise ValueError(f"动画类型必须是以下之一：{', '.join(allowed_animations)}")
        return v
    
    class Config:
        schema_extra = {
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


# ==================== 模板 688003 参数 ====================

class StickerMaterial(BaseModel):
    """贴纸信息"""
    sticker_id: str = Field(..., min_length=1, description="贴纸ID或资源标识")
    position_x: float = Field(0.5, ge=0, le=1, description="水平位置")
    position_y: float = Field(0.5, ge=0, le=1, description="垂直位置")
    scale: float = Field(1.0, ge=0.1, le=5.0, description="缩放比例")
    start_time: float = Field(0, ge=0, description="开始时间（秒）")
    duration: float = Field(..., gt=0, le=300, description="持续时长（秒）")


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
    
    @validator('video_effect')
    def validate_video_effect(cls, v):
        """校验视频特效类型"""
        if v is None:
            return v
        allowed_effects = ['beauty', 'vintage', 'cyberpunk', 'film', 'none']
        if v not in allowed_effects:
            raise ValueError(f"特效类型必须是以下之一：{', '.join(allowed_effects)}")
        return v
    
    @validator('export_quality')
    def validate_export_quality(cls, v):
        """校验导出质量"""
        allowed_qualities = ['720p', '1080p', '2k', '4k']
        if v not in allowed_qualities:
            raise ValueError(f"导出质量必须是以下之一：{', '.join(allowed_qualities)}")
        return v
    
    class Config:
        schema_extra = {
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


# ==================== 响应模型 ====================

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


# ==================== 模板注册表 ====================

# 模板ID到请求参数的映射，用于动态路由处理
TEMPLATE_REGISTRY = {
    "688001": CreateDraftRequest688001,
    "688002": CreateDraftRequest688002,
    "688003": CreateDraftRequest688003,
}


def get_template_request(template_id: str):
    """
    根据模板ID获取对应的请求参数类
    
    Args:
        template_id: 模板ID字符串
        
    Returns:
        对应的请求参数类，如果未找到则返回None
    """
    return TEMPLATE_REGISTRY.get(template_id)


def list_templates() -> List[dict]:
    """
    获取所有可用模板列表
    
    Returns:
        模板信息列表
    """
    templates = [
        {
            "template_id": "688001",
            "name": "视频混剪模板",
            "description": "多视频混剪 + 背景音乐 + 标题文字",
            "supported_features": ["video", "audio", "text", "transition"]
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
