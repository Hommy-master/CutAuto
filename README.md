<div align="center">

**English | [中文](README.zh.md)**

---

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

# cutauto - CapCut Draft Automation Assistant

## Introduction

**cutauto (CapCut Draft Automation Assistant)** is a backend service built with Python + FastAPI, designed to help users quickly generate CapCut video drafts in batches. By loading predefined CapCut templates and replacing the materials within, users can generate a large number of professional-quality video drafts in a short time.

## Features

- **Template Loading**: Support loading CapCut template projects and automatically parsing draft structures
- **Material Replacement**: Support replacing various material types including video, audio, images, and text
- **Multi-track Editing**: Support multi-track editing for video, audio, text, and effect tracks
- **Effect Configuration**: Support video effects, transitions, filters, animations, and other effect configurations
- **Batch Generation**: Quickly generate video drafts in batches through API interfaces
- **Draft Export**: Generate standard CapCut draft formats that can be directly imported into the CapCut client

## Tech Stack

| Component | Version | Description |
|-----------|---------|-------------|
| Python | 3.11+ | Programming Language |
| FastAPI | 0.100+ | Web Framework |
| uv | Latest | Package Manager |
| Docker | - | Containerized Deployment |
| pymediainfo | 7.0+ | Media Information Parser |

## Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the project
git clone <repository-url>
cd cutauto

# Start with Docker Compose (from repository root)
docker compose -f docker/docker-compose.yaml up -d
```

### Option 2: Local Development

```bash
# 1. Install uv
pip install uv

# 2. Install dependencies
uv sync

# 3. Start the service
uv run main.py
```

Once the service is started, access the API at `http://localhost:30000`.

## API Endpoints

### Create Draft

```http
POST /openapi/cutauto/v1/create_draft
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tpl_name | string | Yes | Template name |

**Response Example:**

```json
{
  "draft_url": "https://example.com/openapi/cutauto/v1/get_draft?draft_id=xxx",
  "tip_url": "https://docs.jcaigc.cn/"
}
```

### Create Draft with Specific Template

```http
POST /openapi/cutauto/v1/mashup688001
```

Quickly create a draft using the 688001 template.

## Project Structure

```
cutauto/
├── src/
│   ├── pyJianYingDraft/    # CapCut Draft Core Library
│   │   ├── script_file.py   # Draft file operations
│   │   ├── track.py         # Track management
│   │   ├── segment.py       # Segment management
│   │   └── metadata/        # Effect metadata
│   ├── router/              # API routes
│   ├── service/             # Business logic
│   ├── schemas/             # Data models
│   ├── middlewares/         # Middleware
│   └── utils/               # Utility functions
├── tpls/                    # Template directory
├── main.py                  # Application entry
├── config.py                # Configuration file
├── pyproject.toml           # Project dependencies
└── docker/
    ├── Dockerfile           # Docker image
    └── docker-compose.yaml  # Docker Compose configuration
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DRAFT_URL | - | Draft download URL |
| DOWNLOAD_URL | - | File download URL |
| TIP_URL | - | Help documentation URL |
| DOWNLOAD_FILE_SIZE_LIMIT | 209715200 | File download size limit (bytes) |

## Business Cooperation

For business cooperation inquiries, please contact us:

| Contact | Details |
|---------|---------|
| WeChat | ![WeChat QR Code](wechat.jpg) |
| Email | [taohongmin@sina.cn](mailto:taohongmin@sina.cn) |

## License

This project is open-sourced under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ · cutauto**

</div>
