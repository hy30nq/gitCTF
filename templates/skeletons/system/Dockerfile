FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN mkdir -p /var/ctf && cp flag /var/ctf/flag 2>/dev/null || echo "default" > /var/ctf/flag

EXPOSE 4000

CMD ["socat", "TCP-LISTEN:4000,fork,reuseaddr", "EXEC:python3 /app/service.py"]
