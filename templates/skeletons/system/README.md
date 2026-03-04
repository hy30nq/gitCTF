# 시스템 서비스 스켈레톤

## 구조
```
system/
├── Dockerfile
├── service.py         ← 메인 서비스 (수정 대상)
├── flag               ← 플래그 파일 (빌드 시 /var/ctf/flag로 복사됨)
└── README.md
```

## 빌드 & 실행
```bash
echo "test_flag" > flag
docker build -t my-system-service .
docker run -p 4000:4000 my-system-service
```

## 테스트
```bash
nc localhost 4000
```

## 개발 가이드
1. `service.py`를 수정하여 서비스를 구현하세요.
2. socat이 TCP 연결을 받으면 service.py를 실행합니다.
3. stdin/stdout으로 통신합니다.
4. 플래그는 `/var/ctf/flag` 파일에서 읽습니다.
5. 취약점은 별도 브랜치(bug1, bug2)에 주입하세요.
