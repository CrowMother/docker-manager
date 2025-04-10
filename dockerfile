# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Install dependencies
RUN pip install flask docker

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
