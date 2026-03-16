<div align="center">

**[English](README.md) | 中文**

---

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

# 剪映草稿自动化助手

## 简介

**剪映草稿自动化助手 (CutAuto)** 是一个基于 Python + FastAPI 开发的后端服务，旨在帮助用户快速批量化生成剪映视频草稿。通过加载预定义的剪映模板并替换其中的素材，用户可以在短时间内生成大量专业水准的视频草稿。

## 功能特性

- **模板加载**：支持加载剪映模板工程，自动解析草稿结构
- **素材替换**：支持替换视频、音频、图片、文本等多种素材类型
- **多轨编辑**：支持视频轨、音频轨、文本轨、特效轨等多轨道编辑
- **特效配置**：支持视频特效、转场、滤镜、动画等特效配置
- **批量生成**：通过 API 接口快速批量生成视频草稿
- **草稿导出**：生成标准剪映草稿格式，可直接导入剪映客户端

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.100+ | Web 框架 |
| uv | 最新版 | 包管理工具 |
| Docker | - | 容器化部署 |
| pymediainfo | 7.0+ | 媒体信息解析 |

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd CutAuto

# 使用 Docker Compose 启动
docker-compose up -d
```

### 方式二：本地运行

```bash
# 1. 安装 uv
pip install uv

# 2. 安装依赖
uv sync

# 3. 启动服务
uv run main.py
```

服务启动后，访问 `http://localhost:30000` 即可使用 API。

## API 接口

### 创建草稿

```http
POST /openapi/cutauto/v1/create_draft
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| tpl_name | string | 是 | 模板名称 |

**响应示例：**

```json
{
  "draft_url": "https://example.com/openapi/cutauto/v1/get_draft?draft_id=xxx",
  "tip_url": "https://docs.jcaigc.cn/"
}
```

### 使用指定模板创建草稿

```http
POST /openapi/cutauto/v1/mashup688001
```

使用 688001 模板快速创建草稿。

## 项目结构

```
CutAuto/
├── src/
│   ├── pyJianYingDraft/    # 剪映草稿核心库
│   │   ├── script_file.py   # 草稿文件操作
│   │   ├── track.py         # 轨道管理
│   │   ├── segment.py       # 片段管理
│   │   └── metadata/        # 特效元数据
│   ├── router/              # API 路由
│   ├── service/             # 业务逻辑
│   ├── schemas/             # 数据模型
│   ├── middlewares/         # 中间件
│   └── utils/               # 工具函数
├── tpls/                    # 模板目录
├── main.py                  # 应用入口
├── config.py                # 配置文件
├── pyproject.toml           # 项目依赖
├── Dockerfile               # Docker 镜像
└── docker-compose.yaml      # Docker Compose 配置
```

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DRAFT_URL | - | 草稿下载 URL |
| DOWNLOAD_URL | - | 文件下载 URL |
| TIP_URL | - | 帮助文档 URL |
| DOWNLOAD_FILE_SIZE_LIMIT | 209715200 | 文件下载大小限制（字节）|

## 商业合作

如有商业合作需求，欢迎联系我们：

| 联系方式 | 详情 |
|----------|------|
| 微信 | ![微信二维码](wechat.jpg) |
| 邮箱 | [taohongmin@sina.cn](mailto:taohongmin@sina.cn) |

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**Made with ❤️ for CapCut Automation**

</div>
