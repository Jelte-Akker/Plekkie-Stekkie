FROM python:3.13.3

# Install system dependencies
RUN apt-get update && apt-get install -y wget gnupg && \
    apt-get install -y libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1  libxss1 libasound2 libgbm-dev && \
    apt-get clean

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install-deps
RUN playwright install

COPY app/ ./app

CMD ["python3", "-u", "app/crawler.py"]
