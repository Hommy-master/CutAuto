"""
模板服务层单元测试

测试内容：
1. 处理器工厂的注册和获取
2. 参数验证功能
3. 基础处理器的工具方法
4. 错误处理
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import shutil

from src.service.template import (
    BaseProcessor,
    Processor688001,
    Processor688002,
    Processor688003,
    ProcessorFactory,
    create_draft,
    list_all,
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


# ==================== 处理器工厂测试 ====================

class TestProcessorFactory:
    """处理器工厂测试"""
    
    def test_list_processors(self):
        """测试获取处理器列表"""
        processors = ProcessorFactory.list()
        assert "688001" in processors
        assert "688002" in processors
        assert "688003" in processors
    
    def test_exists_with_valid_template(self):
        """测试存在的模板"""
        assert ProcessorFactory.exists("688001") is True
        assert ProcessorFactory.exists("688002") is True
        assert ProcessorFactory.exists("688003") is True
    
    def test_exists_with_invalid_template(self):
        """测试不存在的模板"""
        assert ProcessorFactory.exists("999999") is False
        assert ProcessorFactory.exists("") is False
    
    def test_get_valid_processor(self):
        """测试获取有效的处理器"""
        processor = ProcessorFactory.get("688001")
        assert isinstance(processor, Processor688001)
        
        processor = ProcessorFactory.get("688002")
        assert isinstance(processor, Processor688002)
        
        processor = ProcessorFactory.get("688003")
        assert isinstance(processor, Processor688003)
    
    def test_get_invalid_processor(self):
        """测试获取无效的处理器"""
        with pytest.raises(CustomException) as exc_info:
            ProcessorFactory.get("999999")
        assert exc_info.value.err == CustomError.RESOURCE_NOT_FOUND
    
    def test_register_new_processor(self):
        """测试注册新处理器"""
        class TestProcessor(BaseProcessor):
            def process(self, params):
                return {}
        
        ProcessorFactory.register("test_template", TestProcessor)
        assert ProcessorFactory.exists("test_template") is True
        
        processor = ProcessorFactory.get("test_template")
        assert isinstance(processor, TestProcessor)
    
    def test_register_invalid_processor(self):
        """测试注册无效的处理器"""
        class NotAProcessor:
            pass
        
        with pytest.raises(ValueError) as exc_info:
            ProcessorFactory.register("invalid", NotAProcessor)
        assert "必须继承 BaseProcessor" in str(exc_info.value)


# ==================== 参数验证测试 ====================

class TestValidateParams:
    """参数验证测试"""
    
    def test_validate_688001_params(self):
        """测试验证 688001 参数"""
        params = {
            "template_id": "688001",
            "videos": [
                {"url": "https://example.com/v1.mp4", "duration": 10}
            ]
        }
        result = validate_params("688001", params)
        assert isinstance(result, CreateDraftRequest688001)
        assert result.template_id == "688001"
    
    def test_validate_688002_params(self):
        """测试验证 688002 参数"""
        params = {
            "template_id": "688002",
            "images": [
                {"url": "https://example.com/i1.jpg", "duration": 5},
                {"url": "https://example.com/i2.jpg", "duration": 5}
            ]
        }
        result = validate_params("688002", params)
        assert isinstance(result, CreateDraftRequest688002)
    
    def test_validate_688003_params(self):
        """测试验证 688003 参数"""
        params = {
            "template_id": "688003",
            "video": {"url": "https://example.com/main.mp4"}
        }
        result = validate_params("688003", params)
        assert isinstance(result, CreateDraftRequest688003)
    
    def test_validate_invalid_template(self):
        """测试验证无效的模板"""
        with pytest.raises(CustomException) as exc_info:
            validate_params("999999", {})
        assert exc_info.value.err == CustomError.PARAM_VALIDATION_FAILED
    
    def test_validate_invalid_params(self):
        """测试验证无效的参数"""
        params = {
            "template_id": "688001",
            "videos": []  # 空数组应该失败
        }
        with pytest.raises(CustomException) as exc_info:
            validate_params("688001", params)
        assert exc_info.value.err == CustomError.PARAM_VALIDATION_FAILED


# ==================== 基础处理器测试 ====================

class TestBaseProcessor:
    """基础处理器测试"""
    
    def test_generate_draft_id_format(self):
        """测试草稿ID格式"""
        processor = BaseProcessor.__new__(BaseProcessor)
        processor.template_id = "688001"
        draft_id = processor._generate_draft_id()
        
        # 应该是 14位时间戳 + 8位随机字符 = 22位
        assert len(draft_id) == 22
        assert draft_id.isalnum()  # 应该只包含字母数字
    
    def test_generate_unique_draft_ids(self):
        """测试生成的草稿ID是唯一的"""
        processor = BaseProcessor.__new__(BaseProcessor)
        processor.template_id = "688001"
        
        ids = [processor._generate_draft_id() for _ in range(10)]
        assert len(set(ids)) == 10  # 所有ID都应该不同


# ==================== 列表功能测试 ====================

class TestListAll:
    """列表功能测试"""
    
    def test_list_all_templates(self):
        """测试获取所有模板"""
        templates = list_all()
        assert len(templates) == 3
        
        # 验证每个模板的结构
        for template in templates:
            assert "template_id" in template
            assert "name" in template
            assert "description" in template
            assert "supported_features" in template


# ==================== 创建草稿集成测试（模拟） ====================

class TestCreateDraft:
    """创建草稿测试（使用模拟）"""
    
    @patch('src.service.template.ProcessorFactory.get')
    def test_create_draft_success(self, mock_get):
        """测试成功创建草稿"""
        # 模拟处理器
        mock_processor = MagicMock()
        mock_processor.create_draft.return_value = {
            "draft_id": "2024032512000012345678",
            "draft_url": "https://example.com/draft",
            "tip_url": "https://docs.example.com",
            "template_id": "688001"
        }
        mock_get.return_value = mock_processor
        
        # 创建请求参数
        params = CreateDraftRequest688001(
            template_id="688001",
            videos=[VideoMaterial(url="https://example.com/v1.mp4")]
        )
        
        # 调用创建草稿
        result = create_draft("688001", params)
        
        # 验证结果
        assert result["draft_id"] == "2024032512000012345678"
        assert result["template_id"] == "688001"
        mock_processor.create_draft.assert_called_once_with(params)
    
    @patch('src.service.template.ProcessorFactory.get')
    def test_create_draft_processor_error(self, mock_get):
        """测试处理器错误"""
        mock_get.side_effect = CustomException(
            CustomError.RESOURCE_NOT_FOUND,
            detail="模板不存在"
        )
        
        params = CreateDraftRequest688001(
            template_id="688001",
            videos=[VideoMaterial(url="https://example.com/v1.mp4")]
        )
        
        with pytest.raises(CustomException) as exc_info:
            create_draft("999999", params)
        assert exc_info.value.err == CustomError.RESOURCE_NOT_FOUND


# ==================== 处理器特定功能测试 ====================

class TestProcessor688001:
    """688001 处理器测试"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = Processor688001()
        assert processor.template_id == "688001"
        assert "688001" in processor.template_path
    
    def test_calculate_duration_with_output_duration(self):
        """测试使用指定的输出时长"""
        processor = Processor688001()
        
        params = CreateDraftRequest688001(
            template_id="688001",
            videos=[
                VideoMaterial(url="https://example.com/v1.mp4", duration=10),
                VideoMaterial(url="https://example.com/v2.mp4", duration=8)
            ],
            output_duration=15.0
        )
        
        duration = processor._calculate_duration(params)
        assert duration == 15.0
    
    def test_calculate_duration_auto(self):
        """测试自动计算时长"""
        processor = Processor688001()
        
        params = CreateDraftRequest688001(
            template_id="688001",
            videos=[
                VideoMaterial(url="https://example.com/v1.mp4", duration=10),
                VideoMaterial(url="https://example.com/v2.mp4", duration=8)
            ]
        )
        
        duration = processor._calculate_duration(params)
        assert duration == 18.0  # 10 + 8


class TestProcessor688002:
    """688002 处理器测试"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = Processor688002()
        assert processor.template_id == "688002"
    
    def test_default_image_display_duration(self):
        """测试默认图片显示时长"""
        params = CreateDraftRequest688002(
            template_id="688002",
            images=[
                ImageMaterial(url="https://example.com/i1.jpg", duration=5),
                ImageMaterial(url="https://example.com/i2.jpg", duration=5)
            ]
        )
        assert params.image_display_duration == 5.0


class TestProcessor688003:
    """688003 处理器测试"""
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        processor = Processor688003()
        assert processor.template_id == "688003"
    
    def test_default_filter_intensity(self):
        """测试默认滤镜强度"""
        params = CreateDraftRequest688003(
            template_id="688003",
            video=VideoMaterial(url="https://example.com/main.mp4")
        )
        assert params.filter_intensity == 0.5
    
    def test_default_export_quality(self):
        """测试默认导出质量"""
        params = CreateDraftRequest688003(
            template_id="688003",
            video=VideoMaterial(url="https://example.com/main.mp4")
        )
        assert params.export_quality == "1080p"


# ==================== 错误处理测试 ====================

class TestErrorHandling:
    """错误处理测试"""
    
    def test_custom_exception_with_detail(self):
        """测试带详细信息的自定义异常"""
        exc = CustomException(
            CustomError.TEMPLATE_NOT_FOUND,
            detail="模板 688001 不存在"
        )
        
        error_dict = exc.err.as_dict(detail=exc.detail)
        assert error_dict["code"] == 2050
        assert "模板 688001 不存在" in error_dict["message"]
    
    def test_custom_exception_without_detail(self):
        """测试不带详细信息的自定义异常"""
        exc = CustomException(CustomError.TEMPLATE_NOT_FOUND)
        
        error_dict = exc.err.as_dict()
        assert error_dict["code"] == 2050
        assert error_dict["message"] == "模板不存在"
    
    def test_custom_exception_english(self):
        """测试英文错误消息"""
        exc = CustomException(CustomError.TEMPLATE_NOT_FOUND)
        
        error_dict = exc.err.as_dict(lang='en')
        assert error_dict["message"] == "Template not found"


# ==================== 边界条件测试 ====================

class TestEdgeCases:
    """边界条件测试"""
    
    def test_688001_exactly_10_videos(self):
        """测试 688001 正好10个视频"""
        videos = [
            VideoMaterial(url=f"https://example.com/v{i}.mp4")
            for i in range(10)
        ]
        params = CreateDraftRequest688001(
            template_id="688001",
            videos=videos
        )
        assert len(params.videos) == 10
    
    def test_688002_exactly_2_images(self):
        """测试 688002 最少2张图片"""
        images = [
            ImageMaterial(url="https://example.com/i1.jpg", duration=5),
            ImageMaterial(url="https://example.com/i2.jpg", duration=5)
        ]
        params = CreateDraftRequest688002(
            template_id="688002",
            images=images
        )
        assert len(params.images) == 2
    
    def test_688002_exactly_20_images(self):
        """测试 688002 最多20张图片"""
        images = [
            ImageMaterial(url=f"https://example.com/i{i}.jpg", duration=5)
            for i in range(20)
        ]
        params = CreateDraftRequest688002(
            template_id="688002",
            images=images
        )
        assert len(params.images) == 20
    
    def test_688003_exactly_20_subtitles(self):
        """测试 688003 最多20条字幕"""
        params = CreateDraftRequest688003(
            template_id="688003",
            video=VideoMaterial(url="https://example.com/main.mp4"),
            subtitles=[
                TextMaterial(content=f"字幕{i}", duration=1)
                for i in range(20)
            ]
        )
        assert len(params.subtitles) == 20
    
    def test_688003_exactly_10_stickers(self):
        """测试 688003 最多10个贴纸"""
        from src.schemas.template import StickerMaterial
        
        params = CreateDraftRequest688003(
            template_id="688003",
            video=VideoMaterial(url="https://example.com/main.mp4"),
            stickers=[
                StickerMaterial(sticker_id=f"sticker_{i}", duration=1)
                for i in range(10)
            ]
        )
        assert len(params.stickers) == 10
