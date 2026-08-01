ARG PYTHON_BASE_IMAGE=python:3.12-bookworm
FROM ${PYTHON_BASE_IMAGE} AS backend-base

ARG DEBIAN_MIRROR=deb.debian.org
ARG DEBIAN_SECURITY_MIRROR=deb.debian.org
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=
ARG PIP_DEFAULT_TIMEOUT=120
ARG PIP_RETRIES=10

ENV PYTHONPATH=/app/src/backend:/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN ((sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list.d/debian.sources && \
      sed -i "s|${DEBIAN_MIRROR}/debian-security|${DEBIAN_SECURITY_MIRROR}/debian-security|g" /etc/apt/sources.list.d/debian.sources) 2>/dev/null || \
     (sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list && \
      sed -i "s|${DEBIAN_MIRROR}/debian-security|${DEBIAN_SECURITY_MIRROR}/debian-security|g" /etc/apt/sources.list)) && \
    apt-get update -o Acquire::Retries=5 && apt-get install -o Acquire::Retries=10 -y --no-install-recommends \
      ca-certificates \
      curl \
      fonts-liberation \
      gcc \
      g++ \
      git \
      libasound2 \
      libatk-bridge2.0-0 \
      libatk1.0-0 \
      libdrm2 \
      libgbm1 \
      libglib2.0-0 \
      libgtk-3-0 \
      libnss3 \
      libx11-xcb1 \
      libxcb-dri3-0 \
      libxcomposite1 \
      libxcursor1 \
      libxdamage1 \
      libxi6 \
      libxrandr2 \
      libxss1 \
      libxtst6 \
      libreoffice \
      chromium \
      chromium-driver \
      pandoc \
      texlive-xetex \
      unzip \
      wget && \
    rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome

COPY requirements.txt .
RUN if [ -n "${PIP_TRUSTED_HOST}" ]; then \
      pip install --no-cache-dir -r requirements.txt -i "${PIP_INDEX_URL}" --trusted-host "${PIP_TRUSTED_HOST}" --timeout "${PIP_DEFAULT_TIMEOUT}" --retries "${PIP_RETRIES}"; \
    else \
      pip install --no-cache-dir -r requirements.txt -i "${PIP_INDEX_URL}" --timeout "${PIP_DEFAULT_TIMEOUT}" --retries "${PIP_RETRIES}"; \
    fi

COPY src/backend/ /app/src/backend/
COPY infra/docker/docker_config.example.yaml /app/zuno/config.yaml
COPY tools/cli/ /app/cli_tools/
COPY tools/scripts/ /app/scripts/
COPY tools/migrations/ /app/migrations/

EXPOSE 7860

CMD ["uvicorn", "--app-dir", "src/backend", "zuno.main:app", "--host", "0.0.0.0", "--port", "7860"]
