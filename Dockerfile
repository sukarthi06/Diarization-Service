# syntax=docker/dockerfile:1
FROM python:3.13-slim

ARG MODEL_NAME=pyannote/speaker-diarization-3.1

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the model weights into the image at build time, so containers don't
# need to download from HuggingFace on every cold start.
RUN --mount=type=secret,id=hf_token \
    python -c "from pyannote.audio import Pipeline; Pipeline.from_pretrained('$MODEL_NAME', token=open('/run/secrets/hf_token').read().strip())"

COPY . .

EXPOSE 50051

CMD ["python", "server.py"]
