FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -e .

COPY app /app/app

ENV DATABASE_URL="sqlite:///./ma_advisory.db"
ENV STORAGE_DIR="/app/storage"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
