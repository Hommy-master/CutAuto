"""
Pytest 配置文件

提供测试用的 fixtures 和配置
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import os
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_video_material():
    """模拟视频素材"""
    return {
        "url": "https://example.com/video.mp4",
        "material_name": "测试视频",
        "start_time": 0,
        "duration": 10.0
    }


@pytest.fixture
def mock_audio_material():
    """模拟音频素材"""
    return {
        "url": "https://example.com/audio.mp3",
        "material_name": "测试音频",
        "volume": 0.8,
        "fade_in": 1.0,
        "fade_out": 2.0
    }


@pytest.fixture
def mock_image_material():
    """模拟图片素材"""
    return {
        "url": "https://example.com/image.jpg",
        "material_name": "测试图片",
        "duration": 5.0
    }


@pytest.fixture
def mock_text_material():
    """模拟文本素材"""
    return {
        "content": "测试文字内容",
        "font_size": 40,
        "color": "#FFFFFF",
        "position_x": 0.5,
        "position_y": 0.2,
        "start_time": 0,
        "duration": 5.0
    }


@pytest.fixture
def valid_688001_request(mock_video_material, mock_audio_material, mock_text_material):
    """有效的 688001 模板请求"""
    return {
        "template_id": "688001",
        "videos": [
            mock_video_material,
            {**mock_video_material, "url": "https://example.com/video2.mp4", "duration": 8.0}
        ],
        "audio": mock_audio_material,
        "title": mock_text_material,
        "transition_type": "fade"
    }


@pytest.fixture
def valid_688002_request(mock_image_material, mock_audio_material):
    """有效的 688002 模板请求"""
    return {
        "template_id": "688002",
        "images": [
            mock_image_material,
            {**mock_image_material, "url": "https://example.com/image2.jpg"},
            {**mock_image_material, "url": "https://example.com/image3.jpg"}
        ],
        "audio": mock_audio_material,
        "animation_type": "ken_burns",
        "image_display_duration": 5.0
    }


@pytest.fixture
def valid_688003_request(mock_video_material, mock_text_material):
    """有效的 688003 模板请求"""
    return {
        "template_id": "688003",
        "video": mock_video_material,
        "subtitles": [
            mock_text_material,
            {**mock_text_material, "content": "第二行字幕", "start_time": 5.0}
        ],
        "video_effect": "vintage",
        "filter_intensity": 0.6,
        "export_quality": "1080p"
    }


@pytest.fixture
def mock_script_file():
    """模拟 ScriptFile 对象"""
    mock_script = MagicMock()
    mock_script.save = MagicMock()
    mock_script.get_imported_track = MagicMock(return_value=MagicMock())
    mock_script.replace_material_by_seg = MagicMock()
    mock_script.replace_text = MagicMock()
    return mock_script


@pytest.fixture
def mock_processor_factory():
    """模拟处理器工厂"""
    with patch('src.service.template.ProcessorFactory') as mock:
        mock.exists.return_value = True
        mock.list.return_value = ["688001", "688002", "688003"]
        yield mock


@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return {
        "test_template_dir": "./test_templates",
        "test_draft_dir": "./test_drafts",
        "test_temp_dir": "./test_temp"
    }


# 配置 pytest
pytest_plugins = []
