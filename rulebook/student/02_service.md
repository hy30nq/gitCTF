# 학생 가이드 2: 서비스 개발

## 서비스 요구사항

1. **Dockerfile 필수**: `docker build`로 빌드 가능해야 함
2. **네트워크 서비스**: TCP 포트 4000에서 리슨
3. **flag 파일**: `/var/ctf/flag`에서 읽어야 함
4. **자동 시작**: `docker run`으로 즉시 서비스 시작

## 서비스 유형

### System 서비스 (socat 기반)
바이너리/스크립트 기반 네트워크 서비스.

```
my-service/
├── Dockerfile
├── flag
└── service.py
```

**Dockerfile 예시:**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y socat
WORKDIR /app
COPY . .
RUN mkdir -p /var/ctf && cp flag /var/ctf/flag
EXPOSE 4000
CMD ["socat", "TCP-LISTEN:4000,fork,reuseaddr", "EXEC:python3 /app/service.py"]
```

**service.py 예시:**
```python
import sys

FLAG_PATH = "/var/ctf/flag"

def read_flag():
    try:
        with open(FLAG_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "NO_FLAG"

def main():
    flag = read_flag()
    print("Welcome to my service!")
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        if line == "GET_FLAG":
            # 이 부분이 취약점!
            print(flag)
        else:
            print(f"Unknown: {line}")

if __name__ == "__main__":
    main()
```

### Web 서비스 (Flask 기반)
HTTP 기반 웹 애플리케이션.

```
my-web-service/
├── Dockerfile
├── flag
├── requirements.txt
└── server.py
```

**Dockerfile 예시:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /var/ctf && cp flag /var/ctf/flag
EXPOSE 4000
CMD ["python", "server.py"]
```

## 로컬 테스트

```bash
# 빌드
docker build -t my-service .

# 실행
docker run -p 4000:4000 my-service

# 다른 터미널에서 접속
nc localhost 4000        # system 서비스
curl http://localhost:4000  # web 서비스
```

## gitctf 검증

```bash
python3 gitctf.py verify-service --team my-team --branch master
```

이 명령은:
1. 팀 레포를 clone
2. master 브랜치에서 Docker build
3. 랜덤 flag를 주입하여 Docker run
4. 서비스가 정상 응답하는지 확인

## 취약점 주입 (Injection Phase)

### 1. bug 브랜치 생성
```bash
cd my-service-repo
git checkout -b bug1
```

### 2. 취약점 코드 삽입
master에는 없는 취약점을 bug1 브랜치에 추가합니다.

### 3. exploit 작성
```
my-exploit/
├── Dockerfile
└── exploit.py
```

**exploit.py 예시:**
```python
import socket
import sys

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    s.recv(1024)  # Welcome 메시지
    s.send(b"GET_FLAG\n")
    flag = s.recv(1024).decode().strip()
    s.close()

    print(flag)  # 마지막 줄에 flag 출력!

if __name__ == "__main__":
    main()
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY exploit.py .
ENTRYPOINT ["python3", "exploit.py"]
```

### 4. exploit 암호화 및 커밋
```bash
# exploit을 zip으로 압축 후 GPG 암호화
# exploit_bug1.zip.pgp 파일을 레포에 커밋
git add exploit_bug1.zip.pgp
git commit -m "Add encrypted exploit for bug1"
git push origin bug1
```

## 중요 규칙

- flag는 반드시 `/var/ctf/flag`에서 읽어야 함
- exploit은 flag 내용을 **stdout 마지막 줄**에 출력해야 함
- 서비스는 TCP 포트 **4000**에서 리슨해야 함
- 자기 팀 서비스에 대한 공격은 **차단**됨
