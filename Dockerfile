FROM python:3.11-slim

WORKDIR /app

# Install dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY app/ app/
COPY tests/ tests/
COPY alembic.ini .
COPY alembic/ alembic/
# Expose the port FastAPI runs on
EXPOSE 8000

# Script para ejecutar migraciones y luego iniciar la app
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000