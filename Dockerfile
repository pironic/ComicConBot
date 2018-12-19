FROM python:3.6-alpine

RUN pip install praw && \
    pip install feedparser

WORKDIR /app

COPY . /app

RUN mkdir -p /app/logs && touch /app/logs/output.log

CMD ["/bin/sh", "-c", "python sidebar.py >&1 | tee /app/logs/output.log"]