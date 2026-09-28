# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for user preferences
RUN mkdir -p /app/user_prefs

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=7861

# Expose port
EXPOSE 7861

# Command to run the application
CMD ["python", "main.py"]
