ARG PYTHON_VERSION=3.12.3
# Builder stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    python -m pip wheel --no-cache-dir --wheel-dir /tmp/wheels -r requirements.txt


FROM python:${PYTHON_VERSION}-slim-bullseye AS runtime
# Runtime stage
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/usr/src/app \
    WHISPER_MODEL=tiny.en \
    MDL_PATH=/usr/src/app/mdl

WORKDIR /usr/src/app

RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /tmp/wheels /tmp/wheels
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir /tmp/wheels/* && \
    rm -rf /tmp/wheels

COPY . .
# Download the Whisper model
RUN mkdir -p ${MDL_PATH} && \
    python - <<'PY'
import os
import whisper

mdl_path = os.environ["MDL_PATH"]
os.makedirs(mdl_path, exist_ok=True)
whisper.load_model(
    name=os.environ["WHISPER_MODEL"],
    download_root=mdl_path,
)
PY

RUN addgroup --system app && adduser --system --ingroup app app
RUN chown -R app:app ${MDL_PATH}
USER app

EXPOSE 8000

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]