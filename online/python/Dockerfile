FROM python:3.7-alpine
COPY . /usr/src/app
COPY crontab /etc/cron.d/scrape
RUN chmod 0644 /etc/cron.d/scrape
RUN service cron start
