# Day 3 solution: container image for the incident report service
FROM python:3.12-slim

# Do not write .pyc files, and print logs straight away
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=local

WORKDIR /app

# Dependencies first: this layer is reused while only the code changes
RUN pip install --no-cache-dir "flask==3.1.*" "gunicorn==23.*"

COPY app ./app

# Run as a normal user, not root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app.main:app"]
