FROM python:3.12-slim AS backend-base

ARG DEBIAN_MIRROR=deb.debian.org
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG CHROME_VERSION=138.0.7204.183

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN (sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i "s|deb.debian.org|${DEBIAN_MIRROR}|g" /etc/apt/sources.list) && \
    apt-get update && apt-get install -y --no-install-recommends \
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
      pandoc \
      texlive-xetex \
      unzip \
      wget && \
    rm -rf /var/lib/apt/lists/*

RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip" && \
    unzip -q chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome && \
    ln -s /opt/chrome/chrome /usr/bin/google-chrome && \
    rm chrome-linux64.zip

RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip -q chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i "${PIP_INDEX_URL}"

COPY src/backend/ .
COPY cli_tools/ /app/cli_tools/
COPY scripts/ /app/scripts/

EXPOSE 7860

CMD ["uvicorn", "agentchat.main:app", "--host", "0.0.0.0", "--port", "7860"]
