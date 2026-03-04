FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git gpg docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lib/ lib/
COPY gitctf.py .
COPY docker/entrypoint-grader.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
