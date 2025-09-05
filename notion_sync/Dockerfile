FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY create_struct.py daily_update.py /app/
RUN mkdir /data
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*
RUN echo "0 0 * * * root python /app/daily_update.py >> /var/log/cron.log 2>&1" > /etc/cron.d/notion-sync
RUN chmod 0644 /etc/cron.d/notion-sync && crontab /etc/cron.d/notion-sync
CMD cron -f
