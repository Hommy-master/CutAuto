"""
模板 688001 请求参数模块

该模板适用于：图片轮播 + 背景音乐
支持替换3张图片和背景音乐
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class CreateDraftRequest688001(BaseModel):
    """
    模板 688001 请求参数
    
    该模板适用于：图片轮播 + 背景音乐
    支持替换3张图片(image1, image2, image3)和背景音乐(bgm)
    
    模板 ID 由路径 `/templates/{template_id}/drafts` 指定，请求体中无需再传 template_id。
    """
    # 第一张图片（必填）
    image1: HttpUrl = Field(
        ...,
        description="第一张图片URL，将替换 9E7AD15B-64B9-40bc-9076-4D555646EFA6.png"
    )
    
    # 第二张图片（必填）
    image2: HttpUrl = Field(
        ...,
        description="第二张图片URL，将替换 AA3EAE10-F30D-4cda-A374-63FA372DA22B.png"
    )
    
    # 第三张图片（必填）
    image3: HttpUrl = Field(
        ...,
        description="第三张图片URL，将替换 F70BB297-6368-432e-983F-378A2C0A38AE.png"
    )
    
    # 背景音乐（可选，不传则使用默认）
    bgm: Optional[HttpUrl] = Field(
        None,
        description="背景音乐URL，将替换 1f48eb595f2664f2fa973975e4767f1d.mp3"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "image1": "https://example.com/image1.jpg",
                "image2": "https://example.com/image2.png",
                "image3": "https://example.com/image3.jpg",
                "bgm": "https://example.com/music.mp3"
            }
        }
    }
