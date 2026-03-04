FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/ctf && cp flag /var/ctf/flag 2>/dev/null || echo "default" > /var/ctf/flag

EXPOSE 4000

CMD ["python", "server.py"]
