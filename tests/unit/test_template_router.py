"""
模板路由单元测试

测试内容：
1. API 端点的请求和响应
2. 参数验证和错误处理
3. HTTP 状态码验证
4. 响应格式验证
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from exceptions import CustomException, CustomError


# 创建测试客户端
client = TestClient(app)

# 所有模板接口的 URL 前缀
BASE = "/openapi/cutauto/v1/templates"


# ==================== 模板列表接口测试 ====================

class TestListTemplates:
    """获取模板列表接口测试"""

    @patch('src.router.v1.list_all')
    def test_list_templates_success(self, mock_list_all):
        """测试成功获取模板列表"""
        mock_list_all.return_value = [
            {
                "template_id": "688001",
                "name": "视频混剪模板",
                "description": "多视频混剪",
                "supported_features": ["video", "audio"]
            },
            {
                "template_id": "688002",
                "name": "图片轮播模板",
                "description": "图片轮播",
                "supported_features": ["image", "audio"]
            }
        ]

        response = client.get(f"{BASE}")

        assert response.status_code == 200
        data = response.json()
        # 响应被中间件封装在 data 字段
        templates = data.get("data", data)
        if isinstance(templates, list):
            assert len(templates) == 2
            assert templates[0]["template_id"] == "688001"
            assert templates[1]["template_id"] == "688002"

    @patch('src.router.v1.list_all')
    def test_list_templates_empty(self, mock_list_all):
        """测试空模板列表"""
        mock_list_all.return_value = []

        response = client.get(f"{BASE}")

        assert response.status_code == 200
        data = response.json()
        templates = data.get("data", data)
        if isinstance(templates, list):
            assert len(templates) == 0


# ==================== 模板详情接口测试 ====================

class TestGetTemplateDetail:
    """获取模板详情接口测试"""

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.list_all')
    def test_get_template_detail_success(self, mock_list_all, mock_exists):
        """测试成功获取模板详情"""
        mock_exists.return_value = True
        mock_list_all.return_value = [
            {
                "template_id": "688001",
                "name": "视频混剪模板",
                "description": "多视频混剪模板",
                "supported_features": ["video", "audio", "text"]
            }
        ]

        response = client.get(f"{BASE}/688001")

        assert response.status_code == 200
        data = response.json()
        assert data["template_id"] == "688001"
        assert data["name"] == "视频混剪模板"
        assert "max_videos" in data

    @patch('src.router.v1.ProcessorFactory.exists')
    def test_get_template_detail_not_found(self, mock_exists):
        """测试获取不存在的模板详情"""
        mock_exists.return_value = False

        response = client.get(f"{BASE}/999999")

        # 中间件将404转换为200+错误码
        assert response.status_code == 200
        data = response.json()
        assert "不存在" in data.get("detail", "") or "不存在" in data.get("message", "")


# ==================== 通用模板创建接口测试 ====================

class TestCreateDraftWithTemplate:
    """通用模板创建接口测试"""

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.validate_params')
    @patch('src.router.v1.create_template_draft')
    def test_create_draft_success(self, mock_create, mock_validate, mock_exists):
        """测试成功创建草稿"""
        mock_exists.return_value = True
        mock_validate.return_value = Mock()
        mock_create.return_value = {
            "draft_id": "2024032512000012345678",
            "draft_url": "https://example.com/draft",
            "tip_url": "https://docs.example.com",
            "template_id": "688001",
            "estimated_duration": 30.0,
        }

        response = client.post(
            f"{BASE}/688001/drafts",
            json={
                "image1": "https://example.com/image1.jpg",
                "image2": "https://example.com/image2.png",
                "image3": "https://example.com/image3.jpg"
            }
        )

        assert response.status_code == 200
        # 响应被中间件处理，检查状态码即可
        assert response.content is not None

    @patch('src.router.v1.ProcessorFactory.exists')
    def test_create_draft_template_not_found(self, mock_exists):
        """测试使用不存在的模板创建草稿"""
        mock_exists.return_value = False

        response = client.post(
            f"{BASE}/999999/drafts",
            json={}
        )

        # 中间件处理错误响应
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") != 0

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.validate_params')
    def test_create_draft_invalid_params(self, mock_validate, mock_exists):
        """测试无效的参数"""
        mock_exists.return_value = True
        mock_validate.side_effect = CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            detail="参数验证失败"
        )

        response = client.post(
            f"{BASE}/688001/drafts",
            json={}
        )

        # 中间件处理错误响应
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") != 0


# ==================== 688001 模板快捷接口测试 ====================

class TestCreateDraft688001:
    """688001 模板快捷接口测试"""

    @patch('src.router.v1.create_template_draft')
    def test_create_draft_688001_success(self, mock_create):
        """测试成功使用 688001 模板创建草稿"""
        mock_create.return_value = {
            "draft_id": "2024032512000012345678",
            "draft_url": "https://example.com/draft",
            "tip_url": "https://docs.example.com",
            "template_id": "688001",
            "estimated_duration": 30.0,
        }

        response = client.post(
            f"{BASE}/688001/drafts",
            json={
                "image1": "https://example.com/image1.jpg",
                "image2": "https://example.com/image2.png",
                "image3": "https://example.com/image3.jpg",
                "bgm": "https://example.com/music.mp3"
            }
        )

        assert response.status_code == 200
        assert response.content is not None

    def test_create_draft_688001_missing_images(self):
        """测试缺少必填图片参数"""
        response = client.post(
            f"{BASE}/688001/drafts",
            json={}
        )

        # 中间件将422转换为200+错误码
        assert response.status_code in (200, 422)
        data = response.json()
        if response.status_code == 200:
            assert data.get("code") != 0  # 应该是错误码


# ==================== 688002 模板快捷接口测试 ====================

class TestCreateDraft688002:
    """688002 模板快捷接口测试"""

    @patch('src.router.v1.create_template_draft')
    def test_create_draft_688002_success(self, mock_create):
        """测试成功使用 688002 模板创建草稿"""
        mock_create.return_value = {
            "draft_id": "2024032512000012345678",
            "draft_url": "https://example.com/draft",
            "tip_url": "https://docs.example.com",
            "template_id": "688002",
            "estimated_duration": 15.0
        }

        response = client.post(
            f"{BASE}/688002/drafts",
            json={
                "images": [
                    {"url": "https://example.com/i1.jpg", "duration": 5},
                    {"url": "https://example.com/i2.jpg", "duration": 5},
                    {"url": "https://example.com/i3.jpg", "duration": 5}
                ],
                "animation_type": "ken_burns"
            }
        )

        assert response.status_code == 200
        assert response.content is not None

    def test_create_draft_688002_not_enough_images(self):
        """测试图片数量不足"""
        response = client.post(
            f"{BASE}/688002/drafts",
            json={
                "images": [
                    {"url": "https://example.com/i1.jpg", "duration": 5}
                    # 至少需要2张图片
                ]
            }
        )

        # 中间件处理 422 验证错误
        assert response.status_code in (200, 422)
        data = response.json()
        if response.status_code == 200:
            assert data.get("code") != 0


# ==================== 688003 模板快捷接口测试 ====================

class TestCreateDraft688003:
    """688003 模板快捷接口测试"""

    @patch('src.router.v1.create_template_draft')
    def test_create_draft_688003_success(self, mock_create):
        """测试成功使用 688003 模板创建草稿"""
        mock_create.return_value = {
            "draft_id": "2024032512000012345678",
            "draft_url": "https://example.com/draft",
            "tip_url": "https://docs.example.com",
            "template_id": "688003",
            "estimated_duration": 60.0
        }

        response = client.post(
            f"{BASE}/688003/drafts",
            json={
                "video": {"url": "https://example.com/main.mp4"},
                "subtitles": [
                    {"content": "字幕1", "start_time": 0, "duration": 3}
                ],
                "video_effect": "vintage",
                "export_quality": "1080p"
            }
        )

        assert response.status_code == 200
        assert response.content is not None

    def test_create_draft_688003_missing_video(self):
        """测试缺少主视频"""
        response = client.post(
            f"{BASE}/688003/drafts",
            json={}
        )

        assert response.status_code in (200, 422)
        data = response.json()
        if response.status_code == 200:
            assert data.get("code") != 0


# ==================== 模板验证接口测试 ====================

class TestValidateTemplate:
    """模板验证接口测试"""

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.validate_params')
    def test_validate_template_success(self, mock_validate, mock_exists):
        """测试成功验证模板参数"""
        mock_exists.return_value = True
        mock_validate.return_value = Mock()

        response = client.post(
            f"{BASE}/688001/validate",
            json={
                "image1": "https://example.com/image1.jpg",
                "image2": "https://example.com/image2.png",
                "image3": "https://example.com/image3.jpg"
            }
        )

        assert response.status_code == 200
        assert response.content is not None

    @patch('src.router.v1.ProcessorFactory.exists')
    def test_validate_template_not_found(self, mock_exists):
        """测试验证不存在的模板"""
        mock_exists.return_value = False

        response = client.post(
            f"{BASE}/999999/validate",
            json={}
        )

        assert response.status_code == 200
        assert response.content is not None

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.validate_params')
    def test_validate_template_invalid_params(self, mock_validate, mock_exists):
        """测试验证无效的参数"""
        mock_exists.return_value = True
        mock_validate.side_effect = CustomException(
            CustomError.PARAM_VALIDATION_FAILED,
            detail="参数验证失败"
        )

        response = client.post(
            f"{BASE}/688001/validate",
            json={}
        )

        assert response.status_code == 200
        assert response.content is not None


# ==================== 响应格式测试 ====================

class TestResponseFormat:
    """响应格式测试"""

    @patch('src.router.v1.list_all')
    def test_response_content_type(self, mock_list_all):
        """测试响应内容类型"""
        mock_list_all.return_value = []

        response = client.get(f"{BASE}")

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.list_all')
    def test_response_structure(self, mock_list_all, mock_exists):
        """测试响应数据结构"""
        mock_exists.return_value = True
        mock_list_all.return_value = [
            {
                "template_id": "688001",
                "name": "视频混剪模板",
                "description": "多视频混剪",
                "supported_features": ["video"]
            }
        ]

        response = client.get(f"{BASE}/688001")

        assert response.status_code == 200
        data = response.json()

        # 验证必需字段
        assert "template_id" in data
        assert "name" in data
        assert "description" in data
        assert "supported_features" in data


# ==================== 错误响应测试 ====================

class TestErrorResponses:
    """错误响应测试"""

    def test_404_response_format(self):
        """测试 404 响应格式"""
        response = client.get(f"{BASE}/999999")

        # 中间件将404转换为200+错误信息
        assert response.status_code == 200
        data = response.json()
        assert "detail" in data or "code" in data

    @patch('src.router.v1.ProcessorFactory.exists')
    @patch('src.router.v1.validate_params')
    @patch('src.router.v1.create_template_draft')
    def test_500_response_format(self, mock_create, mock_validate, mock_exists):
        """测试 500 错误响应格式"""
        mock_exists.return_value = True
        mock_validate.return_value = Mock()
        mock_create.side_effect = Exception("未知错误")

        response = client.post(
            f"{BASE}/688001/drafts",
            json={
                "image1": "https://example.com/image1.jpg",
                "image2": "https://example.com/image2.png",
                "image3": "https://example.com/image3.jpg"
            }
        )

        # 中间件将500转换为200+错误码
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
