FROM python:3.11.11-slim-bookworm
LABEL maintainer="Hudson Bui"

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
COPY ./scripts /scripts
WORKDIR /app
EXPOSE 8000

ARG DEV=false

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    libwebp-dev \
    build-essential \
    linux-headers-amd64 \
    && rm -rf /var/lib/apt/lists/*

# Setup Python environment
RUN python -m venv /py && \
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
