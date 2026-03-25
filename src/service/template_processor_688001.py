"""
模板 688001 处理器模块

该模板适用于：图片轮播 + 背景音乐
支持替换3张图片和背景音乐
"""

import os
import json
import shutil
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

from src.service.template_base import BaseProcessor
from src.schemas.template_688001 import CreateDraftRequest688001
from src.utils.logger import logger
from exceptions import CustomException, CustomError as ErrorCode


class Processor688001(BaseProcessor):
    """
    模板 688001 处理器
    
    处理图片轮播场景，支持：
    - 替换3张图片（image1, image2, image3）
    - 替换背景音乐（bgm）
    - 自动处理文件格式转换
    """
    
    # 模板中的目标文件名映射
    TARGET_FILES = {
        "image1": "9E7AD15B-64B9-40bc-9076-4D555646EFA6.png",
        "image2": "AA3EAE10-F30D-4cda-A374-63FA372DA22B.png",
        "image3": "F70BB297-6368-432e-983F-378A2C0A38AE.png",
        "bgm": "1f48eb595f2664f2fa973975e4767f1d.mp3"
    }
    
    def __init__(self):
        super().__init__("688001")
    
    def process(self, params: CreateDraftRequest688001) -> Dict[str, Any]:
        """
        处理 688001 模板创建请求
        
        Args:
            params: 688001模板参数
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理 688001 模板")
        
        script = None
        try:
            # 1. 复制模板到草稿目录并加载为ScriptFile对象
            script = self._copy_template()
            
            # 2. 下载并替换图片文件
            image_replacements = {}
            for img_key in ["image1", "image2", "image3"]:
                url = getattr(params, img_key)
                target_filename = self.TARGET_FILES[img_key]
                actual_filename = self._download_and_replace_image(url, target_filename)
                image_replacements[target_filename] = actual_filename
            
            # 3. 下载并替换背景音乐（如果提供）
            audio_replacement = None
            if params.bgm:
                audio_replacement = self._download_and_replace_audio(
                    params.bgm, 
                    self.TARGET_FILES["bgm"]
                )
            
            # 4. 更新 draft_content.json 中的路径
            self._update_draft_content(image_replacements, audio_replacement)
            
            # 5. 重新加载并保存ScriptFile（确保同步到draft_info.json）
            if script:
                script.save()
                logger.info(f"ScriptFile 已保存并同步到 draft_info.json")
            
            # 6. 构建响应
            result = self._build_response(estimated_duration=30.0)
            
            logger.info(f"688001 模板处理完成: {result['draft_id']}")
            return result
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"处理 688001 模板失败: {e}")
            raise CustomException(
                ErrorCode.DRAFT_CREATE_ERROR,
                detail=f"模板处理失败: {str(e)}"
            )
        finally:
            self.cleanup()
    
    def _download_and_replace_image(self, url: str, target_filename: str) -> str:
        """
        下载图片并替换模板中的文件
        
        Args:
            url: 图片URL
            target_filename: 目标文件名（模板中的原始文件名）
            
        Returns:
            实际使用的文件名（可能因格式转换而不同）
        """
        logger.info(f"下载图片: {url} -> {target_filename}")
        
        # 下载文件
        downloaded_path = self._download_material(url)
        
        # 获取下载文件的扩展名
        downloaded_ext = os.path.splitext(downloaded_path)[1].lower()
        target_ext = os.path.splitext(target_filename)[1].lower()
        
        # 确定实际使用的文件名
        if downloaded_ext != target_ext:
            # 格式不同，使用下载文件的格式
            actual_filename = os.path.splitext(target_filename)[0] + downloaded_ext
            logger.info(f"图片格式转换: {target_filename} -> {actual_filename}")
        else:
            actual_filename = target_filename
        
        # 复制到草稿目录的 materials/video 文件夹
        dest_dir = os.path.join(self.draft_path, "materials", "video")
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, actual_filename)
        
        shutil.copy2(downloaded_path, dest_path)
        logger.info(f"图片已复制到: {dest_path}")
        
        return actual_filename
    
    def _download_and_replace_audio(self, url: str, target_filename: str) -> str:
        """
        下载音频并替换模板中的文件
        
        Args:
            url: 音频URL
            target_filename: 目标文件名（模板中的原始文件名）
            
        Returns:
            实际使用的文件名（可能因格式转换而不同）
        """
        logger.info(f"下载音频: {url} -> {target_filename}")
        
        # 下载文件
        downloaded_path = self._download_material(url)
        
        # 获取下载文件的扩展名
        downloaded_ext = os.path.splitext(downloaded_path)[1].lower()
        target_ext = os.path.splitext(target_filename)[1].lower()
        
        # 确定实际使用的文件名
        if downloaded_ext != target_ext:
            # 格式不同，使用下载文件的格式
            actual_filename = os.path.splitext(target_filename)[0] + downloaded_ext
            logger.info(f"音频格式转换: {target_filename} -> {actual_filename}")
        else:
            actual_filename = target_filename
        
        # 复制到草稿目录的 audios 文件夹
        dest_dir = os.path.join(self.draft_path, "audios")
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, actual_filename)
        
        shutil.copy2(downloaded_path, dest_path)
        logger.info(f"音频已复制到: {dest_path}")
        
        return actual_filename
    
    def _update_draft_content(self, image_replacements: Dict[str, str], audio_replacement: str = None) -> None:
        """
        更新 draft_content.json 中的文件路径
        
        Args:
            image_replacements: 图片文件名映射 {原文件名: 实际文件名}
            audio_replacement: 音频实际文件名（如果有）
        """
        draft_content_path = os.path.join(self.draft_path, "draft_content.json")
        
        if not os.path.exists(draft_content_path):
            logger.warning(f"draft_content.json 不存在: {draft_content_path}")
            return
        
        # 读取 draft_content.json
        with open(draft_content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换图片路径
        for original_name, actual_name in image_replacements.items():
            if original_name != actual_name:
                # 需要替换文件名
                old_path = f"/materials/video/{original_name}"
                new_path = f"/materials/video/{actual_name}"
                content = content.replace(old_path, new_path)
                logger.info(f"更新图片路径: {old_path} -> {new_path}")
        
        # 替换音频路径
        if audio_replacement:
            original_audio = self.TARGET_FILES["bgm"]
            if original_audio != audio_replacement:
                old_path = f"/audios/{original_audio}"
                new_path = f"/audios/{audio_replacement}"
                content = content.replace(old_path, new_path)
                logger.info(f"更新音频路径: {old_path} -> {new_path}")
        
        # 写回文件
        with open(draft_content_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("draft_content.json 已更新")
