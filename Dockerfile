FROM python:3.13.3

# Install system dependencies
RUN apt-get update && apt-get install -y wget gnupg && \
    apt-get install -y wget ca-certificates fonts-liberation libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libcups2 libxss1 libxtst6 && \
    apt-get clean

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install-deps
RUN playwright install

COPY app/ ./app
COPY .env ./app/.env

CMD ["python3", "-u", "app/crawler.py"]
