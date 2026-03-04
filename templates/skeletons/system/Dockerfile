FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

ENV FLAG="flag{default_flag}"

RUN echo $FLAG > /flag.txt && chmod 400 /flag.txt

EXPOSE 4000

CMD ["socat", "TCP-LISTEN:4000,fork,reuseaddr", "EXEC:python3 /app/service.py"]
