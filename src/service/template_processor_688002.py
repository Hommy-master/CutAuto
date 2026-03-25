"""
模板 688002 处理器模块

该模板适用于：图片轮播 + 背景音乐 + 动态文字
"""

from typing import Any, Dict, List

from src.service.template_base import BaseProcessor
from src.schemas.template_688002 import CreateDraftRequest688002
from src.utils.logger import logger
from exceptions import CustomException, CustomError as ErrorCode


class Processor688002(BaseProcessor):
    """
    模板 688002 处理器
    
    处理图片轮播场景，支持：
    - 2-20张图片素材
    - 背景音乐替换
    - 动态文字添加
    - 图片动画效果（肯伯恩斯等）
    """
    
    def __init__(self):
        super().__init__("688002")
    
    def process(self, params: CreateDraftRequest688002) -> Dict[str, Any]:
        """
        处理 688002 模板创建请求
        
        Args:
            params: 688002模板参数
            
        Returns:
            处理结果字典
        """
        logger.info(f"开始处理 688002 模板，图片数量: {len(params.images)}")
        
        try:
            # 1. 复制模板到草稿目录
            self._copy_template()
            
            # 2. 下载图片素材
            image_paths = self._download_images(params.images)
            
            # 3. 下载音频（如果有）
            audio_path = None
            if params.audio:
                audio_path = self._download_material(str(params.audio.url))
            
            # 4. 处理动态文字
            text_configs = []
            if params.texts:
                text_configs = self._process_texts(params.texts)
            
            # 5. 计算预估时长
            estimated_duration = self._calculate_slideshow_duration(params)
            
            # 6. 生成草稿内容
            self._generate_draft_content(
                images=image_paths,
                audio=audio_path,
                texts=text_configs,
                animation_type=params.animation_type,
                image_display_duration=params.image_display_duration
            )
            
            # 7. 构建响应
            result = self._build_response(estimated_duration)
            
            logger.info(f"688002 模板处理完成: {result['draft_id']}")
            return result
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"处理 688002 模板失败: {e}")
            raise CustomException(
                ErrorCode.DRAFT_CREATE_ERROR,
                detail=f"模板处理失败: {str(e)}"
            )
        finally:
            self.cleanup()
    
    def _download_images(self, images: List[Any]) -> List[str]:
        """
        下载所有图片素材
        
        Args:
            images: 图片素材列表
            
        Returns:
            本地文件路径列表
        """
        paths = []
        for i, image in enumerate(images):
            logger.info(f"下载图片 {i+1}/{len(images)}: {image.url}")
            local_path = self._download_material(str(image.url))
            paths.append(local_path)
        return paths
    
    def _process_texts(self, texts: List[Any]) -> List[Dict[str, Any]]:
        """
        处理动态文字配置
        
        Args:
            texts: 文字配置列表
            
        Returns:
            处理后的文字配置列表
        """
        configs = []
        for text in texts:
            configs.append({
                "content": text.content,
                "font_size": text.font_size,
                "color": text.color,
                "position_x": text.position_x,
                "position_y": text.position_y,
                "start_time": text.start_time,
                "duration": text.duration
            })
        return configs
    
    def _calculate_slideshow_duration(self, params: CreateDraftRequest688002) -> float:
        """
        计算轮播总时长
        
        Args:
            params: 模板参数
            
        Returns:
            总时长（秒）
        """
        # 优先使用配置的单张显示时长
        duration_per_image = params.image_display_duration
        return len(params.images) * duration_per_image
    
    def _generate_draft_content(
        self,
        images: List[str],
        audio: str = None,
        texts: List[Dict[str, Any]] = None,
        animation_type: str = "ken_burns",
        image_display_duration: float = 5.0
    ) -> None:
        """
        生成草稿内容文件
        
        Args:
            images: 图片文件路径列表
            audio: 音频文件路径
            texts: 文字配置列表
            animation_type: 动画类型
            image_display_duration: 单张图片显示时长
        """
        # TODO: 实现草稿内容生成逻辑
        logger.info(
            f"生成草稿内容: {len(images)} 张图片, "
            f"动画: {animation_type}, 单张时长: {image_display_duration}s"
        )
