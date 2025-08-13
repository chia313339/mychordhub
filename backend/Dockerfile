# 後端 Dockerfile - FastAPI + Python
FROM python:3.11-slim

# 設置環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝Poetry
RUN pip install poetry

# 設置工作目錄
WORKDIR /app

# 複製Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 安裝Python依賴
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# 複製應用代碼
COPY . .

# 安裝應用本身
RUN poetry install --only-root

# 創建非root用戶
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 啟動命令
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]