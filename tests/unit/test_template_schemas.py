"""
模板 Schema 单元测试

测试内容：
1. 请求参数模型的创建和验证
2. 字段校验规则（范围、格式、必填等）
3. 自定义验证器功能
4. 响应模型的序列化
"""

import pytest
from pydantic import ValidationError

from src.schemas.template_base import (
    VideoMaterial,
    AudioMaterial,
    ImageMaterial,
    TextMaterial,
    StickerMaterial,
    CreateDraftResponse,
    TemplateInfo,
)
from src.schemas.template_688001 import CreateDraftRequest688001
from src.schemas.template_688002 import CreateDraftRequest688002
from src.schemas.template_688003 import CreateDraftRequest688003
from src.schemas.template_registry import list_templates, get_template_request


# ==================== 基础素材模型测试 ====================

class TestVideoMaterial:
    """视频素材模型测试"""

    def test_valid_video_material(self):
        """测试有效的视频素材"""
        video = VideoMaterial(
            url="https://example.com/video.mp4",
            material_name="测试视频",
            start_time=0,
            duration=10.5
        )
        assert str(video.url).startswith("https://example.com/video.mp4")
        assert video.material_name == "测试视频"
        assert video.start_time == 0
        assert video.duration == 10.5

    def test_video_material_with_only_required_fields(self):
        """测试只传必填字段的视频素材"""
        video = VideoMaterial(url="https://example.com/video.mp4")
        assert str(video.url).startswith("https://example.com/video.mp4")
        assert video.material_name is None
        assert video.start_time == 0
        assert video.duration is None

    def test_invalid_url(self):
        """测试无效的URL"""
        with pytest.raises(ValidationError) as exc_info:
            VideoMaterial(url="not-a-valid-url")
        assert "url" in str(exc_info.value)

    def test_negative_start_time(self):
        """测试负的开始时间"""
        with pytest.raises(ValidationError) as exc_info:
            VideoMaterial(
                url="https://example.com/video.mp4",
                start_time=-1
            )
        assert "start_time" in str(exc_info.value)

    def test_negative_duration(self):
        """测试负的持续时长"""
        with pytest.raises(ValidationError) as exc_info:
            VideoMaterial(
                url="https://example.com/video.mp4",
                duration=-5
            )
        assert "duration" in str(exc_info.value)


class TestAudioMaterial:
    """音频素材模型测试"""

    def test_valid_audio_material(self):
        """测试有效的音频素材"""
        audio = AudioMaterial(
            url="https://example.com/audio.mp3",
            material_name="背景音乐",
            volume=0.8,
            fade_in=1.0,
            fade_out=2.0
        )
        assert audio.volume == 0.8
        assert audio.fade_in == 1.0
        assert audio.fade_out == 2.0

    def test_default_volume(self):
        """测试默认音量"""
        audio = AudioMaterial(url="https://example.com/audio.mp3")
        assert audio.volume == 1.0

    def test_volume_out_of_range(self):
        """测试音量超出范围"""
        with pytest.raises(ValidationError) as exc_info:
            AudioMaterial(
                url="https://example.com/audio.mp3",
                volume=3.0
            )
        assert "volume" in str(exc_info.value)

    def test_negative_fade(self):
        """测试负的淡入淡出时间"""
        with pytest.raises(ValidationError) as exc_info:
            AudioMaterial(
                url="https://example.com/audio.mp3",
                fade_in=-1
            )
        assert "fade_in" in str(exc_info.value)


class TestImageMaterial:
    """图片素材模型测试"""

    def test_valid_image_material(self):
        """测试有效的图片素材"""
        image = ImageMaterial(
            url="https://example.com/image.jpg",
            material_name="封面图",
            duration=5.0
        )
        assert image.duration == 5.0

    def test_duration_too_long(self):
        """测试持续时间过长"""
        with pytest.raises(ValidationError) as exc_info:
            ImageMaterial(
                url="https://example.com/image.jpg",
                duration=400  # 超过300秒限制
            )
        assert "duration" in str(exc_info.value)

    def test_zero_duration(self):
        """测试持续时间为0"""
        with pytest.raises(ValidationError) as exc_info:
            ImageMaterial(
                url="https://example.com/image.jpg",
                duration=0
            )
        assert "duration" in str(exc_info.value)


class TestTextMaterial:
    """文本素材模型测试"""

    def test_valid_text_material(self):
        """测试有效的文本素材"""
        text = TextMaterial(
            content="测试文字",
            font_size=40,
            color="#FFFFFF",
            position_x=0.5,
            position_y=0.2,
            start_time=0,
            duration=5.0
        )
        assert text.content == "测试文字"
        assert text.font_size == 40
        assert text.color == "#FFFFFF"

    def test_default_values(self):
        """测试默认值"""
        text = TextMaterial(content="测试", duration=5.0)
        assert text.font_size == 30
        assert text.color == "#FFFFFF"
        assert text.position_x == 0.5
        assert text.position_y == 0.5

    def test_invalid_color_format(self):
        """测试无效的颜色格式"""
        with pytest.raises(ValidationError) as exc_info:
            TextMaterial(
                content="测试",
                color="red",  # 应该是十六进制格式
                duration=5.0
            )
        assert "color" in str(exc_info.value)

    def test_position_out_of_range(self):
        """测试位置超出范围"""
        with pytest.raises(ValidationError) as exc_info:
            TextMaterial(
                content="测试",
                position_x=1.5,  # 应该在0-1之间
                duration=5.0
            )
        assert "position_x" in str(exc_info.value)

    def test_empty_content(self):
        """测试空内容"""
        with pytest.raises(ValidationError) as exc_info:
            TextMaterial(content="", duration=5.0)
        assert "content" in str(exc_info.value)

    def test_content_too_long(self):
        """测试内容过长"""
        with pytest.raises(ValidationError) as exc_info:
            TextMaterial(content="a" * 501, duration=5.0)
        assert "content" in str(exc_info.value)


# ==================== 模板 688001 请求模型测试 ====================

class TestCreateDraftRequest688001:
    """模板 688001 请求参数测试（图片轮播+背景音乐）"""

    def test_valid_request_all_fields(self):
        """测试完整的有效请求参数"""
        request = CreateDraftRequest688001(
            image1="https://example.com/image1.jpg",
            image2="https://example.com/image2.png",
            image3="https://example.com/image3.jpg",
            bgm="https://example.com/music.mp3"
        )
        assert str(request.image1).startswith("https://example.com/image1.jpg")
        assert str(request.bgm).startswith("https://example.com/music.mp3")

    def test_valid_request_no_bgm(self):
        """测试不传背景音乐（bgm 为可选）"""
        request = CreateDraftRequest688001(
            image1="https://example.com/image1.jpg",
            image2="https://example.com/image2.png",
            image3="https://example.com/image3.jpg"
        )
        assert request.bgm is None

    def test_missing_image1(self):
        """测试缺少 image1（必填）"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688001(
                image2="https://example.com/image2.png",
                image3="https://example.com/image3.jpg"
            )
        assert "image1" in str(exc_info.value)

    def test_missing_image2(self):
        """测试缺少 image2（必填）"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688001(
                image1="https://example.com/image1.jpg",
                image3="https://example.com/image3.jpg"
            )
        assert "image2" in str(exc_info.value)

    def test_missing_image3(self):
        """测试缺少 image3（必填）"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688001(
                image1="https://example.com/image1.jpg",
                image2="https://example.com/image2.png"
            )
        assert "image3" in str(exc_info.value)

    def test_invalid_image_url(self):
        """测试无效的图片URL"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688001(
                image1="not-a-valid-url",
                image2="https://example.com/image2.png",
                image3="https://example.com/image3.jpg"
            )
        assert "image1" in str(exc_info.value)

# ==================== 模板 688002 请求模型测试 ====================

class TestCreateDraftRequest688002:
    """模板 688002 请求参数测试"""

    def test_valid_request(self):
        """测试有效的请求参数"""
        request = CreateDraftRequest688002(
            images=[
                ImageMaterial(url="https://example.com/i1.jpg", duration=5),
                ImageMaterial(url="https://example.com/i2.jpg", duration=5),
                ImageMaterial(url="https://example.com/i3.jpg", duration=5)
            ],
            animation_type="ken_burns",
            image_display_duration=5.0
        )
        assert len(request.images) == 3
        assert request.animation_type == "ken_burns"

    def test_min_images_validation(self):
        """测试最少图片数量验证"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688002(
                images=[ImageMaterial(url="https://example.com/i1.jpg", duration=5)]
                # 至少需要2张图片
            )
        assert "images" in str(exc_info.value)

    def test_max_images_validation(self):
        """测试最多图片数量验证"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688002(
                images=[
                    ImageMaterial(url=f"https://example.com/i{i}.jpg", duration=5)
                    for i in range(21)  # 最多20张图片
                ]
            )
        assert "images" in str(exc_info.value)

    def test_invalid_animation_type(self):
        """测试无效的动画类型"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688002(
                images=[
                    ImageMaterial(url="https://example.com/i1.jpg", duration=5),
                    ImageMaterial(url="https://example.com/i2.jpg", duration=5)
                ],
                animation_type="invalid_animation"
            )
        assert "animation_type" in str(exc_info.value)

    def test_image_display_duration_range(self):
        """测试图片显示时长范围"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688002(
                images=[
                    ImageMaterial(url="https://example.com/i1.jpg", duration=5),
                    ImageMaterial(url="https://example.com/i2.jpg", duration=5)
                ],
                image_display_duration=0.5  # 最小1秒
            )
        assert "image_display_duration" in str(exc_info.value)


# ==================== 模板 688003 请求模型测试 ====================

class TestCreateDraftRequest688003:
    """模板 688003 请求参数测试"""

    def test_valid_request(self):
        """测试有效的请求参数"""
        request = CreateDraftRequest688003(
            video=VideoMaterial(url="https://example.com/main.mp4"),
            subtitles=[
                TextMaterial(content="字幕1", start_time=0, duration=3),
                TextMaterial(content="字幕2", start_time=3, duration=3)
            ],
            stickers=[
                StickerMaterial(sticker_id="sticker_001", duration=5)
            ],
            video_effect="vintage",
            filter_intensity=0.6,
            export_quality="1080p"
        )
        assert request.video_effect == "vintage"
        assert len(request.subtitles) == 2

    def test_required_video_field(self):
        """测试必填的视频字段"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688003()
        assert "video" in str(exc_info.value)

    def test_max_subtitles_validation(self):
        """测试最多字幕数量验证"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688003(
                video=VideoMaterial(url="https://example.com/main.mp4"),
                subtitles=[
                    TextMaterial(content=f"字幕{i}", duration=1)
                    for i in range(21)  # 最多20条字幕
                ]
            )
        assert "subtitles" in str(exc_info.value)

    def test_max_stickers_validation(self):
        """测试最多贴纸数量验证"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688003(
                video=VideoMaterial(url="https://example.com/main.mp4"),
                stickers=[
                    StickerMaterial(sticker_id=f"sticker_{i}", duration=1)
                    for i in range(11)  # 最多10个贴纸
                ]
            )
        assert "stickers" in str(exc_info.value)

    def test_invalid_video_effect(self):
        """测试无效的视频特效"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688003(
                video=VideoMaterial(url="https://example.com/main.mp4"),
                video_effect="invalid_effect"
            )
        assert "video_effect" in str(exc_info.value)

    def test_invalid_export_quality(self):
        """测试无效的导出质量"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688003(
                video=VideoMaterial(url="https://example.com/main.mp4"),
                export_quality="8k"  # 不支持8k
            )
        assert "export_quality" in str(exc_info.value)

    def test_filter_intensity_range(self):
        """测试滤镜强度范围"""
        with pytest.raises(ValidationError) as exc_info:
            CreateDraftRequest688003(
                video=VideoMaterial(url="https://example.com/main.mp4"),
                filter_intensity=1.5  # 应该在0-1之间
            )
        assert "filter_intensity" in str(exc_info.value)


# ==================== 响应模型测试 ====================

class TestCreateDraftResponse:
    """创建草稿响应模型测试"""

    def test_valid_response(self):
        """测试有效的响应"""
        response = CreateDraftResponse(
            code=0,
            message="success",
            draft_url="https://example.com/draft?id=123",
        )
        assert response.code == 0
        assert response.draft_url.startswith("https://example.com/draft")

    def test_default_values(self):
        """测试默认值"""
        response = CreateDraftResponse(
            draft_url="https://example.com/draft?id=123",
        )
        assert response.code == 0
        assert response.message == "success"


class TestTemplateInfo:
    """模板信息响应模型测试"""

    def test_valid_template_info(self):
        """测试有效的模板信息"""
        info = TemplateInfo(
            template_id="688001",
            name="视频混剪模板",
            description="多视频混剪模板",
            supported_features=["video", "audio", "text"],
            max_videos=10,
            max_audios=1
        )
        assert info.template_id == "688001"
        assert info.max_videos == 10


# ==================== 工具函数测试 ====================

class TestListTemplates:
    """模板列表函数测试"""

    def test_list_templates(self):
        """测试获取模板列表"""
        templates = list_templates()
        assert len(templates) == 3

        template_ids = [t["template_id"] for t in templates]
        assert "688001" in template_ids
        assert "688002" in template_ids
        assert "688003" in template_ids

    def test_template_structure(self):
        """测试模板数据结构"""
        templates = list_templates()
        for template in templates:
            assert "template_id" in template
            assert "name" in template
            assert "description" in template
            assert "supported_features" in template
            assert isinstance(template["supported_features"], list)


class TestGetTemplateRequest:
    """获取模板请求类函数测试"""

    def test_get_existing_template(self):
        """测试获取存在的模板"""
        request_class = get_template_request("688001")
        assert request_class is not None
        assert request_class == CreateDraftRequest688001

    def test_get_nonexistent_template(self):
        """测试获取不存在的模板"""
        request_class = get_template_request("999999")
        assert request_class is None

    def test_all_templates_in_registry(self):
        """测试所有模板都在注册表中"""
        templates = list_templates()
        for template in templates:
            request_class = get_template_request(template["template_id"])
            assert request_class is not None, f"模板 {template['template_id']} 未注册"


# ==================== JSON 序列化测试 ====================

class TestJsonSerialization:
    """JSON 序列化测试"""

    def test_video_material_json(self):
        """测试视频素材 JSON 序列化"""
        video = VideoMaterial(
            url="https://example.com/video.mp4",
            material_name="测试视频",
            duration=10.5
        )
        json_data = video.model_dump_json()
        assert "example.com/video.mp4" in json_data
        assert "测试视频" in json_data

    def test_688001_request_json(self):
        """测试 688001 请求参数 JSON 序列化"""
        request = CreateDraftRequest688001(
            image1="https://example.com/image1.jpg",
            image2="https://example.com/image2.png",
            image3="https://example.com/image3.jpg"
        )
        json_data = request.model_dump_json()
        assert "example.com/image1.jpg" in json_data
        assert "image1" in json_data

    def test_response_dict(self):
        """测试响应模型字典转换"""
        response = CreateDraftResponse(
            draft_url="https://example.com/draft",
        )
        data = response.model_dump()
        assert data["code"] == 0
        assert data["draft_url"] == "https://example.com/draft"
