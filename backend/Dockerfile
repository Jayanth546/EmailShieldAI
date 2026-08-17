FROM python:3.14-slim

WORKDIR /app

# Update Debian packages to security-fixed versions
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip "setuptools>=83.0.0" && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade "msgpack>=1.2.1" "setuptools>=83.0.0" && \
    rm -f /usr/local/lib/python3.14/site-packages/pip/_vendor/bom.cdx.json
 
COPY app ./app
COPY ml ./ml

RUN mkdir -p /app/data /app/reports && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
