"""
模板服务模块

本模块实现了可扩展的模板处理器架构，支持：
1. 模板处理器的注册和管理
2. 各模板的独立处理逻辑
3. 统一的草稿创建流程
4. 素材下载和验证
"""

import os
import shutil
import datetime
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, List, Any
from pathlib import Path

import config
import src.pyJianYingDraft as draft
from src.pyJianYingDraft import ScriptFile, TrackType
from src.utils.logger import logger
from src.utils.draft_cache import update_cache
from src.utils.download import download
from src.schemas.template import (
    CreateDraftRequest688001,
    CreateDraftRequest688002,
    CreateDraftRequest688003,
    VideoMaterial,
    AudioMaterial,
    ImageMaterial,
    TextMaterial
)
from exceptions import CustomException, CustomError


# ==================== 基础处理器抽象类 ====================

class BaseProcessor(ABC):
    """
    模板处理器抽象基类
    
    所有具体模板处理器必须继承此类，实现 process 方法。
    提供了通用的草稿创建流程和工具方法。
    """
    
    def __init__(self, template_id: str):
        """
        初始化模板处理器
        
        Args:
            template_id: 模板ID
        """
        self.template_id = template_id
        self.template_path = os.path.join(config.TEMPLATE_DIR, template_id)
        self.draft_id = self._generate_draft_id()
        self.draft_path = os.path.join(config.DRAFT_DIR, self.draft_id)
        self.temp_files: List[str] = []  # 记录临时下载的文件
    
    def _generate_draft_id(self) -> str:
        """
        生成唯一的草稿ID
        
        Returns:
            格式：年月日时分秒 + 8位随机字符
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{timestamp}{unique_id}"
    
    def _copy_template(self) -> None:
        """
        复制模板到草稿目录
        
        Raises:
            CustomException: 模板不存在或复制失败
        """
        if not os.path.exists(self.template_path):
            logger.error(f"模板不存在: {self.template_id}")
            raise CustomException(
                CustomError.RESOURCE_NOT_FOUND,
                detail=f"模板 {self.template_id} 不存在"
            )
        
        # 清理并创建草稿目录
        if os.path.exists(self.draft_path):
            shutil.rmtree(self.draft_path)
        
        try:
            shutil.copytree(self.template_path, self.draft_path)
            logger.info(f"模板复制成功: {self.template_id} -> {self.draft_id}")
        except Exception as e:
            logger.error(f"模板复制失败: {e}")
            raise CustomException(
                CustomError.DRAFT_CREATE_FAILED,
                detail=f"模板复制失败: {str(e)}"
            )
    
    def _load_script(self) -> ScriptFile:
        """
        加载草稿脚本文件
        
        Returns:
            ScriptFile 对象
            
        Raises:
            CustomException: 加载失败
        """
        draft_info_path = os.path.join(self.draft_path, "draft_info.json")
        draft_content_path = os.path.join(self.draft_path, "draft_content.json")
        
        if not os.path.exists(draft_info_path):
            logger.error(f"模板文件不存在: {draft_info_path}")
            raise CustomException(
                CustomError.RESOURCE_NOT_FOUND,
                detail="模板文件缺失"
            )
        
        try:
            script = ScriptFile.load_template(draft_info_path)
            script.dual_file_compatibility = True
            script.save_path = draft_content_path
            return script
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            raise CustomException(
                CustomError.DRAFT_CREATE_FAILED,
                detail=f"加载模板失败: {str(e)}"
            )
    
    def _download_material(self, url: str, material_name: Optional[str] = None) -> str:
        """
        下载素材文件到临时目录
        
        Args:
            url: 素材URL
            material_name: 素材名称
            
        Returns:
            下载后的本地文件路径
            
        Raises:
            CustomException: 下载失败
        """
        try:
            # 使用现有的下载工具
            local_path = download(url, config.TEMP_DIR)
            self.temp_files.append(local_path)
            logger.info(f"素材下载成功: {url} -> {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"素材下载失败: {url}, 错误: {e}")
            raise CustomException(
                CustomError.DOWNLOAD_FILE_FAILED,
                detail=f"下载素材失败: {url}"
            )
    
    def _cleanup_temp_files(self) -> None:
        """清理临时下载的文件"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"清理临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {file_path}, {e}")
    
    def _save_and_cache(self, script: ScriptFile) -> Dict[str, Any]:
        """
        保存草稿并更新缓存
        
        Args:
            script: ScriptFile 对象
            
        Returns:
            包含草稿URL和ID的字典
        """
        try:
            script.save()
            update_cache(self.draft_id, script)
            logger.info(f"草稿保存成功: {self.draft_id}")
            
            return {
                "draft_id": self.draft_id,
                "draft_url": f"{config.DRAFT_URL}?draft_id={self.draft_id}",
                "tip_url": config.TIP_URL
            }
        except Exception as e:
            logger.error(f"保存草稿失败: {e}")
            raise CustomException(
                CustomError.DRAFT_CREATE_FAILED,
                detail=f"保存草稿失败: {str(e)}"
            )
    
    @abstractmethod
    def process(self, params: Any) -> Dict[str, Any]:
        """
        处理模板创建请求（子类必须实现）
        
        Args:
            params: 模板请求参数
            
        Returns:
            包含草稿信息的字典
        """
        pass
    
    def create_draft(self, params: Any) -> Dict[str, Any]:
        """
        统一的草稿创建入口
        
        Args:
            params: 模板请求参数
            
        Returns:
            包含草稿信息的字典
        """
        try:
            # 1. 复制模板
            self._copy_template()
            
            # 2. 处理模板逻辑（由子类实现）
            result = self.process(params)
            
            return result
        finally:
            # 3. 清理临时文件
            self._cleanup_temp_files()


# ==================== 模板 688001 处理器 ====================

class Processor688001(BaseProcessor):
    """
    模板 688001 处理器
    
    功能：多视频混剪 + 背景音乐 + 标题文字
    """
    
    def __init__(self):
        super().__init__("688001")
    
    def process(self, params: CreateDraftRequest688001) -> Dict[str, Any]:
        """
        处理 688001 模板创建请求
        
        Args:
            params: CreateDraftRequest688001 对象
            
        Returns:
            包含草稿信息的字典
        """
        logger.info(f"开始处理模板 688001, 视频数量: {len(params.videos)}")
        
        # 加载脚本
        script = self._load_script()
        
        # 获取主视频轨道
        main_track = script.get_imported_track(TrackType.video, name="main_video")
        
        # 替换视频素材
        for idx, video_info in enumerate(params.videos):
            local_path = self._download_material(str(video_info.url))
            material = draft.VideoMaterial(local_path)
            
            # 计算时间范围
            source_timerange = draft.Timerange(
                int(video_info.start_time * 1000000) if video_info.start_time else 0,
                int(video_info.duration * 1000000) if video_info.duration else material.duration
            )
            
            # 替换素材
            script.replace_material_by_seg(
                track=main_track,
                segment_index=idx,
                material=material,
                source_timerange=source_timerange
            )
            logger.info(f"视频素材替换成功: {idx}, {video_info.material_name or '未命名'}")
        
        # 处理背景音乐
        if params.audio:
            self._process_audio(script, params.audio)
        
        # 处理标题文字
        if params.title:
            self._process_title(script, params.title)
        
        # 保存并返回结果
        result = self._save_and_cache(script)
        result["template_id"] = self.template_id
        result["estimated_duration"] = self._calculate_duration(params)
        
        return result
    
    def _process_audio(self, script: ScriptFile, audio_info: AudioMaterial) -> None:
        """处理背景音乐"""
        local_path = self._download_material(str(audio_info.url))
        material = draft.AudioMaterial(local_path)
        
        # 获取音频轨道
        audio_track = script.get_imported_track(TrackType.audio, name="background_audio")
        
        # 替换音频
        script.replace_material_by_seg(
            track=audio_track,
            segment_index=0,
            material=material
        )
        
        # 设置音量（如果有）
        if audio_info.volume != 1.0:
            # TODO: 实现音量调整
            pass
        
        logger.info(f"背景音乐替换成功: {audio_info.material_name or '未命名'}")
    
    def _process_title(self, script: ScriptFile, title_info: TextMaterial) -> None:
        """处理标题文字"""
        # 获取文本轨道
        text_track = script.get_imported_track(TrackType.text, name="title_text")
        
        # 替换文本内容
        script.replace_text(
            track=text_track,
            segment_index=0,
            text=title_info.content
        )
        
        logger.info(f"标题文字替换成功: {title_info.content[:20]}...")
    
    def _calculate_duration(self, params: CreateDraftRequest688001) -> float:
        """计算预估视频时长"""
        if params.output_duration:
            return params.output_duration
        
        total_duration = 0
        for video in params.videos:
            if video.duration:
                total_duration += video.duration
        
        return total_duration


# ==================== 模板 688002 处理器 ====================

class Processor688002(BaseProcessor):
    """
    模板 688002 处理器
    
    功能：图片轮播 + 背景音乐 + 动态文字
    """
    
    def __init__(self):
        super().__init__("688002")
    
    def process(self, params: CreateDraftRequest688002) -> Dict[str, Any]:
        """
        处理 688002 模板创建请求
        
        Args:
            params: CreateDraftRequest688002 对象
            
        Returns:
            包含草稿信息的字典
        """
        logger.info(f"开始处理模板 688002, 图片数量: {len(params.images)}")
        
        script = self._load_script()
        
        # 获取图片轨道
        image_track = script.get_imported_track(TrackType.video, name="image_sequence")
        
        # 替换图片素材
        for idx, image_info in enumerate(params.images):
            local_path = self._download_material(str(image_info.url))
            material = draft.VideoMaterial(local_path, material_type="photo")
            
            # 设置图片显示时长
            duration_us = int(image_info.duration * 1000000)
            source_timerange = draft.Timerange(0, duration_us)
            
            script.replace_material_by_seg(
                track=image_track,
                segment_index=idx,
                material=material,
                source_timerange=source_timerange
            )
            logger.info(f"图片素材替换成功: {idx}")
        
        # 处理背景音乐
        if params.audio:
            self._process_audio(script, params.audio)
        
        # 处理动态文字
        if params.texts:
            self._process_texts(script, params.texts)
        
        result = self._save_and_cache(script)
        result["template_id"] = self.template_id
        result["estimated_duration"] = len(params.images) * params.image_display_duration
        
        return result
    
    def _process_audio(self, script: ScriptFile, audio_info: AudioMaterial) -> None:
        """处理背景音乐"""
        local_path = self._download_material(str(audio_info.url))
        material = draft.AudioMaterial(local_path)
        
        audio_track = script.get_imported_track(TrackType.audio, name="background_audio")
        script.replace_material_by_seg(
            track=audio_track,
            segment_index=0,
            material=material
        )
        logger.info("背景音乐替换成功")
    
    def _process_texts(self, script: ScriptFile, texts: List[TextMaterial]) -> None:
        """处理动态文字"""
        text_track = script.get_imported_track(TrackType.text, name="dynamic_texts")
        
        for idx, text_info in enumerate(texts):
            if idx < len(text_track.segments):
                script.replace_text(
                    track=text_track,
                    segment_index=idx,
                    text=text_info.content
                )
        
        logger.info(f"动态文字替换成功: {len(texts)} 条")


# ==================== 模板 688003 处理器 ====================

class Processor688003(BaseProcessor):
    """
    模板 688003 处理器
    
    功能：单视频 + 特效 + 贴纸 + 字幕
    """
    
    def __init__(self):
        super().__init__("688003")
    
    def process(self, params: CreateDraftRequest688003) -> Dict[str, Any]:
        """
        处理 688003 模板创建请求
        
        Args:
            params: CreateDraftRequest688003 对象
            
        Returns:
            包含草稿信息的字典
        """
        logger.info("开始处理模板 688003")
        
        script = self._load_script()
        
        # 替换主视频
        self._process_main_video(script, params.video)
        
        # 处理字幕
        if params.subtitles:
            self._process_subtitles(script, params.subtitles)
        
        # 处理贴纸
        if params.stickers:
            self._process_stickers(script, params.stickers)
        
        # 应用视频特效
        if params.video_effect:
            self._apply_video_effect(script, params.video_effect, params.filter_intensity)
        
        result = self._save_and_cache(script)
        result["template_id"] = self.template_id
        
        # 计算预估时长
        if params.video.duration:
            result["estimated_duration"] = params.video.duration
        
        return result
    
    def _process_main_video(self, script: ScriptFile, video_info: VideoMaterial) -> None:
        """处理主视频"""
        local_path = self._download_material(str(video_info.url))
        material = draft.VideoMaterial(local_path)
        
        main_track = script.get_imported_track(TrackType.video, name="main_video")
        
        source_timerange = draft.Timerange(
            int(video_info.start_time * 1000000) if video_info.start_time else 0,
            int(video_info.duration * 1000000) if video_info.duration else material.duration
        )
        
        script.replace_material_by_seg(
            track=main_track,
            segment_index=0,
            material=material,
            source_timerange=source_timerange
        )
        logger.info("主视频替换成功")
    
    def _process_subtitles(self, script: ScriptFile, subtitles: List[TextMaterial]) -> None:
        """处理字幕"""
        subtitle_track = script.get_imported_track(TrackType.text, name="subtitles")
        
        for idx, subtitle in enumerate(subtitles):
            if idx < len(subtitle_track.segments):
                script.replace_text(
                    track=subtitle_track,
                    segment_index=idx,
                    text=subtitle.content
                )
        
        logger.info(f"字幕替换成功: {len(subtitles)} 条")
    
    def _process_stickers(self, script: ScriptFile, stickers: List[Any]) -> None:
        """处理贴纸"""
        # TODO: 实现贴纸处理逻辑
        logger.info(f"贴纸处理: {len(stickers)} 个")
    
    def _apply_video_effect(self, script: ScriptFile, effect_type: str, intensity: float) -> None:
        """应用视频特效"""
        # TODO: 实现特效应用逻辑
        logger.info(f"应用特效: {effect_type}, 强度: {intensity}")


# ==================== 处理器工厂 ====================

class ProcessorFactory:
    """
    模板处理器工厂类
    
    用于注册和获取模板处理器，实现处理器的动态管理。
    """
    
    # 处理器注册表
    _processors: Dict[str, Type[BaseProcessor]] = {
        "688001": Processor688001,
        "688002": Processor688002,
        "688003": Processor688003,
    }
    
    @classmethod
    def register(cls, template_id: str, processor_class: Type[BaseProcessor]) -> None:
        """
        注册新的模板处理器
        
        Args:
            template_id: 模板ID
            processor_class: 处理器类，必须继承 BaseProcessor
        """
        if not issubclass(processor_class, BaseProcessor):
            raise ValueError("处理器类必须继承 BaseProcessor")
        
        cls._processors[template_id] = processor_class
        logger.info(f"模板处理器注册成功: {template_id}")
    
    @classmethod
    def get(cls, template_id: str) -> BaseProcessor:
        """
        获取模板处理器实例
        
        Args:
            template_id: 模板ID
            
        Returns:
            处理器实例
            
        Raises:
            CustomException: 模板不存在
        """
        processor_class = cls._processors.get(template_id)
        if not processor_class:
            logger.error(f"模板处理器未找到: {template_id}")
            raise CustomException(
                CustomError.RESOURCE_NOT_FOUND,
                detail=f"模板 {template_id} 不存在或未注册"
            )
        
        return processor_class()
    
    @classmethod
    def list(cls) -> List[str]:
        """
        获取所有已注册的模板ID列表
        
        Returns:
            模板ID列表
        """
        return list(cls._processors.keys())
    
    @classmethod
    def exists(cls, template_id: str) -> bool:
        """
        检查模板是否受支持
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否支持
        """
        return template_id in cls._processors


# ==================== 对外服务接口 ====================

def create_draft(template_id: str, params: Any) -> Dict[str, Any]:
    """
    创建模板草稿的统一入口
    
    Args:
        template_id: 模板ID
        params: 模板请求参数
        
    Returns:
        包含草稿信息的字典
        
    Raises:
        CustomException: 创建失败
    """
    # 获取处理器
    processor = ProcessorFactory.get(template_id)
    
    # 执行创建
    return processor.create_draft(params)


def list_all() -> List[Dict[str, Any]]:
    """
    获取支持的模板列表
    
    Returns:
        模板信息列表
    """
    from src.schemas.template import list_templates
    return list_templates()


def validate_params(template_id: str, params: dict) -> Any:
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
    from src.schemas.template import get_template_request
    
    request_class = get_template_request(template_id)
    if not request_class:
        raise CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            detail=f"未知的模板ID: {template_id}"
        )
    
    try:
        return request_class(**params)
    except Exception as e:
        raise CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            detail=str(e)
        )
