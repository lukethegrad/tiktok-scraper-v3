# Use slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
    libpangocairo-1.0-0 libx11-xcb1 libxext6 libxi6 libxrandr2 \
    libxtst6 --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy local files into container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright Chromium
RUN playwright install chromium

# Expose port 8080 (used by Fly.io)
EXPOSE 8080

# Start the Flask app
CMD ["python", "app.py"]
