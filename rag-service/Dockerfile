FROM python:3.14-slim

WORKDIR /app

COPY requirements-prod.txt .

RUN pip install --no-cache-dir -r requirements-prod.txt

COPY app/ ./app/

EXPOSE 7860

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]