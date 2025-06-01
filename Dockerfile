# Use a slim Python image
FROM python:3.10-slim

# Install ExifTool and required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your FastAPI app will run on
EXPOSE 8000

# Run your main application
CMD ["python", "main.py"]
