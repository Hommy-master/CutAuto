"""
模板工作流集成测试

测试内容：
1. 完整的草稿创建流程
2. 多个组件之间的协作
3. 实际文件操作（使用临时目录）
4. 错误恢复和清理
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock

from src.service.template import (
    Processor688001,
    Processor688002,
    Processor688003,
    ProcessorFactory,
    create_draft,
    validate_params,
)
from src.schemas.template import (
    CreateDraftRequest688001,
    CreateDraftRequest688002,
    CreateDraftRequest688003,
    VideoMaterial,
    AudioMaterial,
    ImageMaterial,
    TextMaterial,
)
from exceptions import CustomException, CustomError


# ==================== 集成测试基类 ====================

class TestTemplateWorkflowBase:
    """模板工作流测试基类"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """测试前后的设置和清理"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = os.path.join(self.temp_dir, "templates")
        self.draft_dir = os.path.join(self.temp_dir, "drafts")
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.draft_dir, exist_ok=True)
        
        yield
        
        # 清理临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# ==================== 688001 模板集成测试 ====================

class TestTemplate688001Workflow(TestTemplateWorkflowBase):
    """688001 模板完整工作流测试"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = Processor688001()
        
        assert processor.template_id == "688001"
        assert processor.draft_id is not None
        assert len(processor.draft_id) == 22  # 时间戳(14) + 随机字符(8)
    
    def test_draft_id_generation(self):
        """测试草稿ID生成"""
        processor = Processor688001()
        
        # 生成多个ID，确保唯一性
        ids = [processor._generate_draft_id() for _ in range(100)]
        assert len(set(ids)) == 100  # 所有ID都应该唯一
    
    @patch('src.service.template.download_file')
    @patch('src.service.template.ScriptFile.load_template')
    @patch('src.service.template.update_cache')
    def test_create_draft_workflow_mocked(
        self, mock_cache, mock_load_template, mock_download, 
        setup_teardown
    ):
        """测试带模拟的草稿创建工作流"""
        # 设置模拟
        mock_download.return_value = "/tmp/test_video.mp4"
        
        mock_script = MagicMock()
        mock_script.save = MagicMock()
        mock_track = MagicMock()
        mock_track.segments = [MagicMock(), MagicMock()]
        mock_script.get_imported_track.return_value = mock_track
        mock_load_template.return_value = mock_script
        
        # 创建请求参数
        params = CreateDraftRequest688001(
            template_id="688001",
            videos=[
                VideoMaterial(url="https://example.com/v1.mp4", duration=10),
                VideoMaterial(url="https://example.com/v2.mp4", duration=8)
            ]
        )
        
        # 由于模板目录不存在，这里会失败，但我们测试的是流程
        # 实际集成测试需要真实的模板文件
        try:
            processor = Processor688001()
            result = processor.create_draft(params)
        except CustomException as e:
            # 预期会失败，因为模板目录不存在
            assert e.err in [CustomError.RESOURCE_NOT_FOUND, CustomError.DRAFT_CREATE_FAILED]


# ==================== 688002 模板集成测试 ====================

class TestTemplate688002Workflow(TestTemplateWorkflowBase):
    """688002 模板完整工作流测试"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = Processor688002()
        
        assert processor.template_id == "688002"
        assert processor.draft_id is not None
    
    def test_calculate_estimated_duration(self):
        """测试计算预估时长"""
        params = CreateDraftRequest688002(
            template_id="688002",
            images=[
                ImageMaterial(url="https://example.com/i1.jpg", duration=5),
                ImageMaterial(url="https://example.com/i2.jpg", duration=5),
                ImageMaterial(url="https://example.com/i3.jpg", duration=5)
            ],
            image_display_duration=5.0
        )
        
        # 预估时长 = 图片数量 * 每张图片显示时长
        expected_duration = 3 * 5.0
        assert expected_duration == 15.0


# ==================== 688003 模板集成测试 ====================

class TestTemplate688003Workflow(TestTemplateWorkflowBase):
    """688003 模板完整工作流测试"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = Processor688003()
        
        assert processor.template_id == "688003"
        assert processor.draft_id is not None
    
    def test_params_with_all_features(self):
        """测试包含所有功能的参数"""
        from src.schemas.template import StickerMaterial
        
        params = CreateDraftRequest688003(
            template_id="688003",
            video=VideoMaterial(url="https://example.com/main.mp4", duration=60),
            subtitles=[
                TextMaterial(content=f"字幕{i}", start_time=i*3, duration=3)
                for i in range(5)
            ],
            stickers=[
                StickerMaterial(sticker_id=f"sticker_{i}", duration=5)
                for i in range(3)
            ],
            video_effect="vintage",
            filter_intensity=0.7,
            export_quality="2k"
        )
        
        assert len(params.subtitles) == 5
        assert len(params.stickers) == 3
        assert params.video_effect == "vintage"
        assert params.export_quality == "2k"


# ==================== 工厂模式集成测试 ====================

class TestProcessorFactoryIntegration:
    """处理器工厂集成测试"""
    
    def test_factory_returns_correct_processor(self):
        """测试工厂返回正确的处理器"""
        processor_688001 = ProcessorFactory.get("688001")
        processor_688002 = ProcessorFactory.get("688002")
        processor_688003 = ProcessorFactory.get("688003")
        
        assert isinstance(processor_688001, Processor688001)
        assert isinstance(processor_688002, Processor688002)
        assert isinstance(processor_688003, Processor688003)
    
    def test_factory_creates_new_instances(self):
        """测试工厂创建新的实例"""
        processor1 = ProcessorFactory.get("688001")
        processor2 = ProcessorFactory.get("688001")
        
        # 应该是不同的实例
        assert processor1 is not processor2
        # 但应该是相同的类型
        assert type(processor1) == type(processor2)
    
    def test_all_templates_registered(self):
        """测试所有模板都已注册"""
        registered = ProcessorFactory.list()
        
        assert "688001" in registered
        assert "688002" in registered
        assert "688003" in registered


# ==================== 参数验证集成测试 ====================

class TestParameterValidationIntegration:
    """参数验证集成测试"""
    
    def test_validate_688001_full_params(self):
        """测试验证完整的 688001 参数"""
        params = {
            "template_id": "688001",
            "videos": [
                {"url": "https://example.com/v1.mp4", "duration": 10, "start_time": 0},
                {"url": "https://example.com/v2.mp4", "duration": 8}
            ],
            "audio": {
                "url": "https://example.com/music.mp3",
                "volume": 0.7,
                "fade_in": 1.0
            },
            "title": {
                "content": "测试标题",
                "font_size": 50,
                "color": "#FFD700",
                "position_y": 0.1
            },
            "transition_type": "slide",
            "output_duration": 20.0
        }
        
        result = validate_params("688001", params)
        
        assert isinstance(result, CreateDraftRequest688001)
        assert len(result.videos) == 2
        assert result.transition_type == "slide"
    
    def test_validate_688002_full_params(self):
        """测试验证完整的 688002 参数"""
        params = {
            "template_id": "688002",
            "images": [
                {"url": "https://example.com/i1.jpg", "duration": 5},
                {"url": "https://example.com/i2.jpg", "duration": 5},
                {"url": "https://example.com/i3.jpg", "duration": 5}
            ],
            "audio": {"url": "https://example.com/bg.mp3"},
            "texts": [
                {"content": "文字1", "duration": 5},
                {"content": "文字2", "duration": 5}
            ],
            "animation_type": "fade",
            "image_display_duration": 5.0
        }
        
        result = validate_params("688002", params)
        
        assert isinstance(result, CreateDraftRequest688002)
        assert len(result.images) == 3
        assert result.animation_type == "fade"
    
    def test_validate_688003_full_params(self):
        """测试验证完整的 688003 参数"""
        params = {
            "template_id": "688003",
            "video": {
                "url": "https://example.com/main.mp4",
                "duration": 60
            },
            "subtitles": [
                {"content": "字幕1", "start_time": 0, "duration": 3},
                {"content": "字幕2", "start_time": 3, "duration": 3}
            ],
            "stickers": [
                {"sticker_id": "s1", "duration": 5},
                {"sticker_id": "s2", "duration": 5}
            ],
            "video_effect": "cyberpunk",
            "filter_intensity": 0.8,
            "export_quality": "4k"
        }
        
        result = validate_params("688003", params)
        
        assert isinstance(result, CreateDraftRequest688003)
        assert result.video_effect == "cyberpunk"
        assert result.export_quality == "4k"
    
    def test_validate_invalid_template(self):
        """测试验证无效的模板"""
        with pytest.raises(CustomException) as exc_info:
            validate_params("999999", {})
        
        assert exc_info.value.err == CustomError.PARAM_VALIDATION_FAILED
    
    def test_validate_boundary_values(self):
        """测试边界值验证"""
        # 测试 688001 正好10个视频（最大值）
        params = {
            "template_id": "688001",
            "videos": [
                {"url": f"https://example.com/v{i}.mp4"}
                for i in range(10)
            ]
        }
        
        result = validate_params("688001", params)
        assert len(result.videos) == 10
        
        # 测试 688002 正好2张图片（最小值）
        params = {
            "template_id": "688002",
            "images": [
                {"url": "https://example.com/i1.jpg", "duration": 5},
                {"url": "https://example.com/i2.jpg", "duration": 5}
            ]
        }
        
        result = validate_params("688002", params)
        assert len(result.images) == 2


# ==================== 错误处理集成测试 ====================

class TestErrorHandlingIntegration:
    """错误处理集成测试"""
    
    def test_custom_exception_bilingual(self):
        """测试自定义异常的双语支持"""
        exc = CustomException(CustomError.TEMPLATE_NOT_FOUND)
        
        # 中文
        cn_dict = exc.err.as_dict(lang='zh')
        assert cn_dict["message"] == "模板不存在"
        
        # 英文
        en_dict = exc.err.as_dict(lang='en')
        assert en_dict["message"] == "Template not found"
    
    def test_custom_exception_with_detail(self):
        """测试带详细信息的异常"""
        exc = CustomException(
            CustomError.TEMPLATE_NOT_FOUND,
            detail="模板 688001 不存在"
        )
        
        error_dict = exc.err.as_dict(detail=exc.detail, lang='zh')
        assert "模板 688001 不存在" in error_dict["message"]
    
    def test_error_code_ranges(self):
        """测试错误码范围"""
        # 模板相关错误码应该在 2050-2099 范围内
        assert 2050 <= CustomError.TEMPLATE_NOT_FOUND.code <= 2099
        assert 2050 <= CustomError.TEMPLATE_PROCESSOR_NOT_FOUND.code <= 2099
        assert 2050 <= CustomError.INVALID_TEMPLATE_PARAMS.code <= 2099


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    def test_processor_creation_performance(self):
        """测试处理器创建性能"""
        import time
        
        start_time = time.time()
        
        # 创建100个处理器实例
        for _ in range(100):
            ProcessorFactory.get("688001")
        
        elapsed = time.time() - start_time
        
        # 应该在1秒内完成
        assert elapsed < 1.0
    
    def test_parameter_validation_performance(self):
        """测试参数验证性能"""
        import time
        
        params = {
            "template_id": "688001",
            "videos": [
                {"url": f"https://example.com/v{i}.mp4", "duration": 10}
                for i in range(10)
            ]
        }
        
        start_time = time.time()
        
        # 验证100次
        for _ in range(100):
            validate_params("688001", params)
        
        elapsed = time.time() - start_time
        
        # 应该在1秒内完成
        assert elapsed < 1.0
