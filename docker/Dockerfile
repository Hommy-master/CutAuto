FROM python:3.11-slim

# 使用pip安装uv
RUN pip install --no-cache-dir uv

# 验证uv安装
RUN uv --version

# 复制文件（构建上下文为仓库根目录，CI 在根目录生成 _ROOT_/app）
COPY _ROOT_/ .

# 设置工作目录
WORKDIR /app

# 创建非root用户并提前配置缓存目录
RUN mkdir -p /root/.cache/uv

# 安装依赖（仍使用root用户确保权限）
RUN uv sync

# 暴露应用端口
EXPOSE 30000

# 设置环境变量，指定uv缓存目录和用户主目录
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:/app/bin:$PATH" \
    HOME="/root" \
    UV_CACHE_DIR="/root/.cache/uv"

# 启动命令
CMD ["uv", "run", "main.py", "--workers", "4"]
