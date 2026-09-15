FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STOCKFORGE_WEB_UPLOAD_ROOT=/app/runtime/web-references \
    STOCKFORGE_WEB_DATABASE=/app/runtime/web-jobs.sqlite \
    STOCKFORGE_PROVIDER_ROOT=/app/runtime/provider \
    STOCKFORGE_WORKER_INTERVAL=2 \
    PORT=7860

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/app.py

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
