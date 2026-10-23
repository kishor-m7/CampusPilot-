# CampusPilot Production Container Definition
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY backend /app/backend
COPY supabase /app/supabase

EXPOSE 8000
EXPOSE 8001

# Default startup command (runs FastAPI with embedded Streamable HTTP MCP)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
