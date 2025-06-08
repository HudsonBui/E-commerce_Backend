# FROM nvidia/cuda:12.9.0-cudnn-devel-ubuntu20.04
# FROM python:3.11.11-slim-bookworm
FROM tensorflow/tensorflow:latest-gpu
LABEL maintainer="Hudson Bui"

ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
COPY ./scripts /scripts
WORKDIR /app
EXPOSE 8000

ARG DEV=false

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends\
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    postgresql-client \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    libwebp-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setup Python environment
RUN python3 -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp/requirements.txt /tmp/requirements.dev.txt  # Clean up temp files

# Setup user and directories
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

CMD ["run.sh"]
