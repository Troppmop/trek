# Use an official lightweight Python image
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for Postgres and building packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ... (Builder stage stays the same)

# Final Stage
FROM python:3.12-slim
WORKDIR /app

# --- ADD THIS SECTION ---
# Install ONLY the runtime library needed for Postgres
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
# -------------------------

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy app code
COPY . . 

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]