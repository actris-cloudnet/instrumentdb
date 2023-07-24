FROM python:3.10 AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000

FROM base AS dev
COPY requirements_dev.txt .
RUN pip install --no-cache-dir -r requirements_dev.txt
CMD ["./entrypoint.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS prod
RUN pip install --no-cache-dir gunicorn==20.1
COPY . .
CMD ["./entrypoint.sh", "gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
