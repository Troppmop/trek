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

# Final Stage
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Update PATH to include the local pip installs
ENV PATH=/root/.local/bin:$PATH

# Expose FastAPI port
EXPOSE 8000

# Run with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]