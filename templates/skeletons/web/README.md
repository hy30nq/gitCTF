# 웹 서비스 스켈레톤

## 구조
```
web/
├── Dockerfile
├── requirements.txt
├── server.py          ← 메인 서비스 (수정 대상)
└── README.md
```

## 빌드 & 실행
```bash
docker build -t my-web-service .
docker run -p 4000:4000 -e FLAG="flag{test_flag}" my-web-service
```

## 개발 가이드
1. `server.py`를 수정하여 서비스 기능을 구현하세요.
2. `/api/flag` 엔드포인트에 적절한 인증/보안을 추가하세요.
3. 취약점은 별도 브랜치(bug1, bug2)에 주입하세요.
