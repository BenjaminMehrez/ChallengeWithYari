FROM python:3.11-slim


WORKDIR /app


# Install dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the project file
COPY app/ app/
COPY tests/ tests/


# Expose the port FastAPI runs on
EXPOSE 8000

RUN "uvicorn app.main:app --host 0.0.0.0 --port 8000"