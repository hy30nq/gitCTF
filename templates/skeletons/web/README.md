# 웹 서비스 스켈레톤

## 구조
```
web/
├── Dockerfile
├── requirements.txt
├── server.py          ← 메인 서비스 (수정 대상)
├── flag               ← 플래그 파일 (빌드 시 /var/ctf/flag로 복사됨)
└── README.md
```

## 빌드 & 실행
```bash
echo "test_flag" > flag
docker build -t my-web-service .
docker run -p 4000:4000 my-web-service
```

## 개발 가이드
1. `server.py`를 수정하여 서비스 기능을 구현하세요.
2. `/api/flag` 엔드포인트에 적절한 인증/보안을 추가하세요.
3. 플래그는 `/var/ctf/flag`에서 읽습니다.
4. 취약점은 별도 브랜치(bug1, bug2)에 주입하세요.
