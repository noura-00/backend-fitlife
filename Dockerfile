# Base image
FROM python:3.10

# Set working directory
WORKDIR /usr/src/backend

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose application port
EXPOSE 8000

# Define default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
