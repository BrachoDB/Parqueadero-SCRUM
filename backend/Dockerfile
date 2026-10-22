FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PARQUEADERO_DB_PATH=/data/parqueadero.db

WORKDIR /app

RUN useradd --system --uid 10001 --create-home app \
    && mkdir -p /app/database /data \
    && chown -R app:app /app /data

COPY backend/requirements-prod.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=app:app backend/ /app/backend/

USER app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
