"""
模板 688001 处理器模块

该模板适用于：多视频混剪 + 背景音乐 + 标题文字
"""

from typing import Any, Dict, List

from src.service.template_base import BaseProcessor
from src.schemas.template_688001 import CreateDraftRequest688001
from src.utils.logger import logger
from exceptions import CustomException, CustomError as ErrorCode


class Processor688001(BaseProcessor):
    """
    模板 688001 处理器
    
    处理多视频混剪场景，支持：
    - 最多10个视频素材
    - 背景音乐替换
    - 标题文字自定义
    - 转场效果选择
    """
    
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
        logger.info(f"开始处理 688001 模板，视频数量: {len(params.videos)}")
        
        try:
            # 1. 复制模板到草稿目录
            self._copy_template()
            
            # 2. 下载视频素材
            video_paths = self._download_videos(params.videos)
            
            # 3. 下载音频（如果有）
            audio_path = None
            if params.audio:
                audio_path = self._download_material(str(params.audio.url))
            
            # 4. 处理标题文字
            title_config = None
            if params.title:
                title_config = self._process_title(params.title)
            
            # 5. 计算预估时长
            estimated_duration = self._calculate_video_duration(params)
            
            # 6. 生成草稿内容
            self._generate_draft_content(
                videos=video_paths,
                audio=audio_path,
                title=title_config,
                transition_type=params.transition_type or "fade"
            )
            
            # 7. 构建响应
            result = self._build_response(estimated_duration)
            
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
    
    def _download_videos(self, videos: List[Any]) -> List[str]:
        """
        下载所有视频素材
        
        Args:
            videos: 视频素材列表
            
        Returns:
            本地文件路径列表
        """
        paths = []
        for i, video in enumerate(videos):
            logger.info(f"下载视频 {i+1}/{len(videos)}: {video.url}")
            local_path = self._download_material(str(video.url))
            paths.append(local_path)
        return paths
    
    def _process_title(self, title: Any) -> Dict[str, Any]:
        """
        处理标题文字配置
        
        Args:
            title: 标题文字配置
            
        Returns:
            处理后的标题配置
        """
        return {
            "content": title.content,
            "font_size": title.font_size,
            "color": title.color,
            "position_x": title.position_x,
            "position_y": title.position_y,
            "start_time": title.start_time,
            "duration": title.duration
        }
    
    def _calculate_video_duration(self, params: CreateDraftRequest688001) -> float:
        """
        计算视频总时长
        
        Args:
            params: 模板参数
            
        Returns:
            总时长（秒）
        """
        total = 0.0
        for video in params.videos:
            if video.duration:
                total += video.duration
        return total or 30.0  # 默认30秒
    
    def _generate_draft_content(
        self,
        videos: List[str],
        audio: str = None,
        title: Dict[str, Any] = None,
        transition_type: str = "fade"
    ) -> None:
        """
        生成草稿内容文件
        
        Args:
            videos: 视频文件路径列表
            audio: 音频文件路径
            title: 标题配置
            transition_type: 转场类型
        """
        # TODO: 实现草稿内容生成逻辑
        # 这里应该调用 pyJianYingDraft 相关功能生成 draft_content.json
        logger.info(f"生成草稿内容: {len(videos)} 个视频, 转场: {transition_type}")
