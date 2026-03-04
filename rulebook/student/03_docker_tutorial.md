# 참가자 가이드 — 3. Docker 기초 튜토리얼

## Docker란?

애플리케이션을 컨테이너라는 격리된 환경에서 실행하는 기술입니다.
GitCTF에서는 **모든 서비스와 익스플로잇이 Docker 컨테이너 안에서** 실행됩니다.

## Docker Desktop 설치

- [Windows/Mac](https://www.docker.com/products/docker-desktop/)
- Linux: `sudo apt install docker.io docker-compose-plugin`

설치 확인:
```bash
docker --version
docker compose version
```

## Dockerfile 작성법

### 서비스 Dockerfile 예시
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# 환경변수로 플래그를 주입받음
ENV FLAG="flag{default}"

EXPOSE 4000
CMD ["python", "server.py"]
```

### 익스플로잇 Dockerfile 예시
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY exploit.py .

# 실행 스크립트 생성
RUN echo '#!/bin/sh\npython /app/exploit.py $1 $2' > /bin/exploit && chmod +x /bin/exploit

ENTRYPOINT ["/bin/exploit"]
```

## 필수 명령어

```bash
# 이미지 빌드
docker build -t my-service .

# 컨테이너 실행
docker run -p 4000:4000 -e FLAG="flag{test}" my-service

# 실행 중인 컨테이너 확인
docker ps

# 컨테이너 중지
docker stop CONTAINER_ID

# 로그 확인
docker logs CONTAINER_ID
```

## 익스플로잇 테스트

```bash
# 1. 서비스 실행
docker run -d --name target -p 4000:4000 -e FLAG="flag{test_abc}" my-service

# 2. 익스플로잇 빌드 & 실행
docker build -t my-exploit ./exploit/
docker run --network host my-exploit localhost 4000

# 3. 출력에 flag{test_abc}가 표시되면 성공!
```

> ⚠️ **중요**: 로컬 환경에서 직접 실행하지 마세요!
> 반드시 Docker 컨테이너 안에서 동작하는지 확인하세요.
> 로컬에서만 동작하고 Docker에서 안 되는 경우가 많습니다.
