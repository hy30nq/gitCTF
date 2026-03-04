# 시스템 서비스 스켈레톤

## 구조
```
system/
├── Dockerfile
├── service.py         ← 메인 서비스 (수정 대상)
└── README.md
```

## 빌드 & 실행
```bash
docker build -t my-system-service .
docker run -p 4000:4000 -e FLAG="flag{test_flag}" my-system-service
```

## 테스트
```bash
nc localhost 4000
```

## 개발 가이드
1. `service.py`를 수정하여 서비스를 구현하세요.
2. socat이 TCP 연결을 받으면 service.py를 실행합니다.
3. stdin/stdout으로 통신합니다.
4. 플래그는 `/flag.txt` 또는 환경변수 `FLAG`에 저장됩니다.
