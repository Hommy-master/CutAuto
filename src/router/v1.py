"""
V1 路由模块

本模块实现了所有 V1 版本的 API 接口，包括：
1. 基础草稿创建接口
2. 基于模板的草稿创建接口（支持 688001、688002、688003 等模板）
3. 模板查询接口
4. 模板参数验证接口
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Body, Path

from src.schemas.template_base import CreateDraftResponse, TemplateInfo
from src.schemas.template_688001 import CreateDraftRequest688001
from src.schemas.template_688002 import CreateDraftRequest688002
from src.schemas.template_688003 import CreateDraftRequest688003
from src.schemas.template_registry import list_templates, get_template_request
from src.service.template_factory import (
    create_draft as create_template_draft,
    list_all,
    validate_params,
    ProcessorFactory
)
from src.utils.logger import logger
from exceptions import CustomException
import config


# 创建路由实例
router = APIRouter(prefix="/v1", tags=["v1"])

@router.get(
    path="/templates",
    response_model=List[TemplateInfo],
    summary="获取模板列表",
    description="获取所有可用的剪映模板列表及其基本信息"
)
async def get_template_list() -> List[TemplateInfo]:
    """
    获取所有可用模板列表
    
    Returns:
        模板信息列表
    """
    logger.info("获取模板列表")
    
    templates = list_all()
    
    # 转换为响应模型
    result = []
    for tpl in templates:
        result.append(TemplateInfo(
            template_id=tpl["template_id"],
            name=tpl["name"],
            description=tpl["description"],
            supported_features=tpl["supported_features"]
        ))
    
    return result


@router.get(
    path="/templates/{template_id}",
    response_model=TemplateInfo,
    summary="获取模板详情",
    description="获取指定模板的详细信息"
)
async def get_template_detail(
    template_id: str = Path(..., description="模板ID，如：688001、688002、688003")
) -> TemplateInfo:
    """
    获取指定模板的详细信息
    
    Args:
        template_id: 模板ID
        
    Returns:
        模板详细信息
        
    Raises:
        HTTPException: 模板不存在
    """
    logger.info(f"获取模板详情: {template_id}")
    
    # 检查模板是否支持
    if not ProcessorFactory.exists(template_id):
        raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")
    
    # 获取模板信息
    templates = list_all()
    template_info = next(
        (t for t in templates if t["template_id"] == template_id),
        None
    )
    
    if not template_info:
        raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")
    
    # 根据模板ID添加特定的限制信息
    limits = _get_template_limits(template_id)
    
    return TemplateInfo(
        template_id=template_info["template_id"],
        name=template_info["name"],
        description=template_info["description"],
        supported_features=template_info["supported_features"],
        **limits
    )


def _get_template_limits(template_id: str) -> Dict[str, int]:
    """
    获取模板的资源限制
    
    Args:
        template_id: 模板ID
        
    Returns:
        资源限制字典
    """
    limits = {
        "688001": {"max_videos": 10, "max_audios": 1, "max_texts": 5},
        "688002": {"max_images": 20, "max_audios": 1, "max_texts": 5},
        "688003": {"max_videos": 1, "max_texts": 20},
    }
    return limits.get(template_id, {})


# ==================== 模板创建接口 ====================

@router.post(
    path="/templates/{template_id}/drafts",
    response_model=CreateDraftResponse,
    summary="使用模板创建草稿",
    description="使用指定模板创建剪映草稿，支持 688001、688002、688003 等模板"
)
async def create_draft_with_template(
    template_id: str = Path(..., description="模板ID，如：688001、688002、688003"),
    params: Dict[str, Any] = Body(
        ...,
        description="模板参数（不含 template_id，模板由 URL 路径中的 template_id 指定），根据模板类型不同而不同",
    )
) -> CreateDraftResponse:
    """
    使用指定模板创建剪映草稿
    
    模板 ID 仅取自 URL 路径，请求体中不需要、也不应再传 template_id。
    
    根据不同模板ID，需要传入不同的参数：
    - 688001: 视频混剪模板，需要传入 videos、audio、title 等参数
    - 688002: 图片轮播模板，需要传入 images、audio、texts 等参数
    - 688003: 视频特效模板，需要传入 video、subtitles、stickers 等参数
    
    Args:
        template_id: 模板ID
        params: 模板参数
        
    Returns:
        草稿创建结果
        
    Raises:
        HTTPException: 参数错误或创建失败
    """
    logger.info(f"使用模板创建草稿: {template_id}")
    
    try:
        # 1. 验证模板是否支持
        if not ProcessorFactory.exists(template_id):
            raise HTTPException(
                status_code=404,
                detail={
                    "code": 1002,
                    "message": f"模板 {template_id} 不存在",
                    "available_templates": ProcessorFactory.list()
                }
            )
        
        # 2. 验证并解析参数
        validated_params = validate_params(template_id, params)
        logger.info(f"参数验证通过: {template_id}")
        
        # 3. 创建草稿
        result = create_template_draft(template_id, validated_params)
        logger.info(f"草稿创建成功: {result['draft_id']}")
        
        # 4. 返回响应
        return CreateDraftResponse(
            code=0,
            message="success",
            draft_url=result["draft_url"],
            draft_id=result["draft_id"],
            tip_url=result["tip_url"],
            template_id=result["template_id"],
            estimated_duration=result.get("estimated_duration")
        )
        
    except CustomException as e:
        # 处理业务异常
        logger.error(f"创建草稿失败: {e.err.cn_message}")
        raise HTTPException(
            status_code=400,
            detail=e.err.as_dict(detail=e.detail)
        )
    except Exception as e:
        # 处理未知异常
        logger.error(f"创建草稿时发生未知错误: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": 9999,
                "message": "创建草稿失败，请稍后重试"
            }
        )


# ==================== 特定模板的快捷接口 ====================

@router.post(
    path="/templates/688001/drafts",
    response_model=CreateDraftResponse,
    summary="使用 688001 模板创建草稿（视频混剪）",
    description="视频混剪模板：支持多视频 + 背景音乐 + 标题文字"
)
async def create_draft_688001(
    params: CreateDraftRequest688001 = Body(..., description="688001模板参数")
) -> CreateDraftResponse:
    """
    使用 688001 模板创建草稿（视频混剪模板）
    
    该模板适用于图片轮播场景，支持：
    - 替换3张图片素材（image1, image2, image3）
    - 替换背景音乐（bgm）
    - 自动处理文件格式转换
    
    Args:
        params: 688001模板参数
        
    Returns:
        草稿创建结果
    """
    logger.info(f"使用 688001 模板创建草稿")
    
    try:
        result = create_template_draft("688001", params)
        
        return CreateDraftResponse(
            code=0,
            message="success",
            draft_url=result["draft_url"],
            draft_id=result["draft_id"],
            tip_url=result["tip_url"],
            template_id="688001",
            estimated_duration=result.get("estimated_duration")
        )
        
    except CustomException as e:
        logger.error(f"创建草稿失败: {e.err.cn_message}")
        raise HTTPException(
            status_code=400,
            detail=e.err.as_dict(detail=e.detail)
        )


@router.post(
    path="/templates/688002/drafts",
    response_model=CreateDraftResponse,
    summary="使用 688002 模板创建草稿（图片轮播）",
    description="图片轮播模板：支持多张图片 + 背景音乐 + 动态文字"
)
async def create_draft_688002(
    params: CreateDraftRequest688002 = Body(..., description="688002模板参数")
) -> CreateDraftResponse:
    """
    使用 688002 模板创建草稿（图片轮播模板）
    
    该模板适用于图片轮播场景，支持：
    - 2-20张图片素材
    - 背景音乐替换
    - 动态文字添加
    - 图片动画效果（肯伯恩斯等）
    
    Args:
        params: 688002模板参数
        
    Returns:
        草稿创建结果
    """
    logger.info(f"使用 688002 模板创建草稿")
    
    try:
        result = create_template_draft("688002", params)
        
        return CreateDraftResponse(
            code=0,
            message="success",
            draft_url=result["draft_url"],
            draft_id=result["draft_id"],
            tip_url=result["tip_url"],
            template_id="688002",
            estimated_duration=result.get("estimated_duration")
        )
        
    except CustomException as e:
        logger.error(f"创建草稿失败: {e.err.cn_message}")
        raise HTTPException(
            status_code=400,
            detail=e.err.as_dict(detail=e.detail)
        )


@router.post(
    path="/templates/688003/drafts",
    response_model=CreateDraftResponse,
    summary="使用 688003 模板创建草稿（视频特效）",
    description="视频特效模板：支持单视频 + 特效 + 贴纸 + 字幕"
)
async def create_draft_688003(
    params: CreateDraftRequest688003 = Body(..., description="688003模板参数")
) -> CreateDraftResponse:
    """
    使用 688003 模板创建草稿（视频特效模板）
    
    该模板适用于单视频编辑场景，支持：
    - 主视频替换
    - 字幕添加（最多20条）
    - 贴纸添加（最多10个）
    - 视频特效（美颜、复古、赛博朋克等）
    
    Args:
        params: 688003模板参数
        
    Returns:
        草稿创建结果
    """
    logger.info("使用 688003 模板创建草稿")
    
    try:
        result = create_template_draft("688003", params)
        
        return CreateDraftResponse(
            code=0,
            message="success",
            draft_url=result["draft_url"],
            draft_id=result["draft_id"],
            tip_url=result["tip_url"],
            template_id="688003",
            estimated_duration=result.get("estimated_duration")
        )
        
    except CustomException as e:
        logger.error(f"创建草稿失败: {e.err.cn_message}")
        raise HTTPException(
            status_code=400,
            detail=e.err.as_dict(detail=e.detail)
        )


# ==================== 模板验证接口 ====================

@router.post(
    path="/templates/{template_id}/validate",
    response_model=Dict[str, Any],
    summary="验证模板参数",
    description="验证模板参数是否合法，不实际创建草稿"
)
async def validate_template(
    template_id: str = Path(..., description="模板ID"),
    params: Dict[str, Any] = Body(
        ...,
        description="待验证的模板参数（不含 template_id，模板由路径中的 template_id 指定）",
    )
) -> Dict[str, Any]:
    """
    验证模板参数
    
    用于在实际创建草稿前验证参数是否合法。模板 ID 仅取自 URL 路径。
    
    Args:
        template_id: 模板ID
        params: 待验证的参数
        
    Returns:
        验证结果
    """
    logger.info(f"验证模板参数: {template_id}")
    
    # 检查模板是否支持
    if not ProcessorFactory.exists(template_id):
        return {
            "valid": False,
            "code": 1002,
            "message": f"模板 {template_id} 不存在"
        }
    
    try:
        # 验证参数
        validated_params = validate_params(template_id, params)
        
        return {
            "valid": True,
            "code": 0,
            "message": "参数验证通过",
            "template_id": template_id,
            "params_summary": {
                "template_id": template_id
            }
        }
        
    except CustomException as e:
        return {
            "valid": False,
            "code": e.err.code,
            "message": e.err.cn_message,
            "detail": e.detail
        }
    except Exception as e:
        return {
            "valid": False,
            "code": 9999,
            "message": f"参数验证失败: {str(e)}"
        }
