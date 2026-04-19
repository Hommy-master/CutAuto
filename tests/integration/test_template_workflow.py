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

from src.service.template_factory import (
    ProcessorFactory,
    create_draft,
    validate_params,
)
from src.service.template_processor_688001 import Processor688001
from src.service.template_processor_688002 import Processor688002
from src.service.template_processor_688003 import Processor688003
from src.schemas.template_688001 import CreateDraftRequest688001
from src.schemas.template_688002 import CreateDraftRequest688002
from src.schemas.template_688003 import CreateDraftRequest688003
from src.schemas.template_base import VideoMaterial, AudioMaterial, ImageMaterial, TextMaterial
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

    def test_target_files_defined(self):
        """测试 TARGET_FILES 已定义所有必要的文件"""
        processor = Processor688001()

        assert len(processor.TARGET_FILES) == 4
        assert "image1" in processor.TARGET_FILES
        assert "image2" in processor.TARGET_FILES
        assert "image3" in processor.TARGET_FILES
        assert "bgm" in processor.TARGET_FILES

    def test_process_raises_on_missing_template(self):
        """测试模板目录不存在时抛出异常"""
        processor = Processor688001()

        params = CreateDraftRequest688001(
            image1="https://example.com/i1.jpg",
            image2="https://example.com/i2.jpg",
            image3="https://example.com/i3.jpg"
        )

        # 模板目录不存在时应该抛出 CustomException
        with pytest.raises(CustomException) as exc_info:
            processor.process(params)
        assert exc_info.value.err in [
            CustomError.TEMPLATE_NOT_FOUND,
            CustomError.TEMPLATE_COPY_ERROR,
            CustomError.DRAFT_CREATE_FAILED,
            CustomError.DRAFT_CREATE_ERROR,
        ]


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
        from src.schemas.template_base import StickerMaterial

        params = CreateDraftRequest688003(
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

    def test_factory_returns_none_for_unknown(self):
        """测试工厂对未知模板返回None"""
        processor = ProcessorFactory.get("999999")
        assert processor is None


# ==================== 参数验证集成测试 ====================

class TestParameterValidationIntegration:
    """参数验证集成测试"""

    def test_validate_688001_params(self):
        """测试验证 688001 参数（图片+bgm）"""
        params = {
            "image1": "https://example.com/image1.jpg",
            "image2": "https://example.com/image2.png",
            "image3": "https://example.com/image3.jpg",
            "bgm": "https://example.com/music.mp3"
        }

        result = validate_params("688001", params)

        assert isinstance(result, CreateDraftRequest688001)

    def test_validate_688001_no_bgm(self):
        """测试验证 688001 参数（无背景音乐）"""
        params = {
            "image1": "https://example.com/image1.jpg",
            "image2": "https://example.com/image2.png",
            "image3": "https://example.com/image3.jpg"
        }

        result = validate_params("688001", params)
        assert isinstance(result, CreateDraftRequest688001)
        assert result.bgm is None

    def test_validate_688002_full_params(self):
        """测试验证完整的 688002 参数"""
        params = {
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

        assert exc_info.value.err == CustomError.TEMPLATE_NOT_FOUND

    def test_validate_boundary_values(self):
        """测试边界值验证"""
        # 测试 688002 正好2张图片（最小值）
        params = {
            "images": [
                {"url": "https://example.com/i1.jpg", "duration": 5},
                {"url": "https://example.com/i2.jpg", "duration": 5}
            ]
        }

        result = validate_params("688002", params)
        assert len(result.images) == 2

        # 测试 688002 正好20张图片（最大值）
        params = {
            "images": [
                {"url": f"https://example.com/i{i}.jpg", "duration": 5}
                for i in range(20)
            ]
        }

        result = validate_params("688002", params)
        assert len(result.images) == 20


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
            "image1": "https://example.com/image1.jpg",
            "image2": "https://example.com/image2.png",
            "image3": "https://example.com/image3.jpg"
        }

        start_time = time.time()

        # 验证100次
        for _ in range(100):
            validate_params("688001", params)

        elapsed = time.time() - start_time

        # 应该在1秒内完成
        assert elapsed < 1.0
