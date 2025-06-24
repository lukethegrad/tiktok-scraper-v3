
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y wget gnupg libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libgtk-3-0 libxdamage1 libgbm1

RUN pip install --upgrade pip && pip install -r requirements.txt && playwright install chromium

EXPOSE 8080
CMD ["python", "app.py"]
