# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Set environment variables to prevent generating .pyc files and to run Python unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

# Install Python dependencies
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the application's code into the container
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script which applies migrations and starts Gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]