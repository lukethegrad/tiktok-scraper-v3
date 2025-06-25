# Use the official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg curl \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libxss1 libasound2 libxtst6 libxrandr2 \
    libxdamage1 libxcomposite1 libxfixes3 libxkbcommon0 \
    libdbus-1-3 libx11-xcb1 libxi6 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . .

# Install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright and its dependencies
RUN playwright install --with-deps

# Expose the Flask port
EXPOSE 8080

# Run the Flask app
CMD ["python", "app.py"]
