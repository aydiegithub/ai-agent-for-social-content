# --- Stage 1: Build Stage ---
# Use an official Python runtime as a parent image
FROM python:3.11-slim as builder

# Set environment variables to prevent Python from writing .pyc files
# and to ensure output is sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by Python packages like psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install Python dependencies
# First, copy only the requirements file to leverage Docker's layer caching.
# This step will only be re-run if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Stage ---
# Use a clean, minimal Python image for the final container
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the rest of the application code
COPY . .

# Run collectstatic to gather all static files into the STATIC_ROOT directory
# This is done here so it's part of the final container image.
RUN python manage.py collectstatic --noinput

# Expose the port that gunicorn will run on.
# Cloud Run will automatically use this port.
EXPOSE 8080

# The command to run the application using gunicorn.
# This is the production-grade server that will handle web requests.
# The --bind 0.0.0.0:$PORT command is required by Cloud Run.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 project.wsgi:application