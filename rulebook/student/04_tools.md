# 학생 가이드 4: 도구 사용법

## Git 기본

### 레포 클론
```bash
git clone https://github.com/org/repo-name.git
cd repo-name
```

### 브랜치 관리
```bash
# 브랜치 목록 확인
git branch -a

# 새 브랜치 생성
git checkout -b bug1

# 브랜치 전환
git checkout master

# 원격 브랜치 가져오기
git fetch origin
git checkout -b bug1 origin/bug1
```

### 커밋 & 푸시
```bash
git add .
git commit -m "설명"
git push origin branch-name
```

## Docker 기본

### 이미지 빌드
```bash
docker build -t my-image .
```

### 컨테이너 실행
```bash
# 포트 매핑
docker run -p 4000:4000 my-image

# 백그라운드 실행
docker run -d -p 4000:4000 --name my-container my-image

# 환경변수 전달
docker run -e FLAG=test_flag my-image
```

### 컨테이너 관리
```bash
# 실행 중인 컨테이너 확인
docker ps

# 로그 확인
docker logs my-container

# 컨테이너 중지/삭제
docker stop my-container
docker rm my-container

# 이미지 삭제
docker rmi my-image
```

### 네트워크 접속 (exploit에서)
```bash
# 호스트 네트워크 사용 (서비스가 localhost에서 실행 중일 때)
docker run --network host my-exploit 127.0.0.1 4000
```

## GPG 기본

### 키 생성
```bash
gpg --full-generate-key
# RSA, 4096bit 권장
```

### 키 확인
```bash
# 공개키 목록
gpg --list-keys --keyid-format short

# 비밀키 목록
gpg --list-secret-keys --keyid-format short
```

### 키 내보내기/가져오기
```bash
# 공개키 내보내기 (강사에게 전달)
gpg --armor --export YOUR_KEY_ID > my-pubkey.asc

# 다른 사람의 공개키 가져오기
gpg --import teammate-pubkey.asc
```

### 암호화/복호화
```bash
# 암호화 (여러 수신자)
gpg --encrypt --recipient KEY_ID1 --recipient KEY_ID2 file.zip

# 복호화
gpg --decrypt file.zip.gpg > file.zip
```

## gitctf.py 전체 명령어

### 참가자용

```bash
# 서비스 검증
python3 gitctf.py verify-service --team TEAM --branch BRANCH [--conf CONFIG]

# 익스플로잇 검증
python3 gitctf.py verify-exploit \
  --exploit EXPLOIT_DIR \
  --service-dir SERVICE_DIR \
  --branch BRANCH \
  --timeout SECONDS \
  [--encrypt] [--conf CONFIG]

# 익스플로잇 제출
python3 gitctf.py submit \
  --exploit EXPLOIT_DIR \
  --service-dir SERVICE_DIR \
  --branch BRANCH \
  --target TARGET_TEAM \
  [--conf CONFIG]

# 익스플로잇 다운로드
python3 gitctf.py fetch \
  --team TEAM --issue ISSUE_NO \
  [--conf CONFIG]

# 점수 확인
python3 gitctf.py score [--conf CONFIG]

# 서비스 로컬 실행
python3 gitctf.py exec-service --team TEAM --branch BRANCH [--conf CONFIG]

# 익스플로잇 로컬 실행
python3 gitctf.py exec-exploit \
  --exploit EXPLOIT_DIR \
  --ip IP --port PORT --timeout SECONDS
```

### 공통 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--conf` | config.json 경로 | `config.json` |
| `--token` | GitHub PAT | `$GITHUB_TOKEN` 환경변수 |

## 디렉토리 구조 규칙

### 서비스 디렉토리
```
service/
├── Dockerfile      # 필수
├── flag            # 기본 flag (빌드 시 /var/ctf/flag로 복사)
├── service.py      # 서비스 코드
└── (기타 파일)
```

### 익스플로잇 디렉토리
```
exploit/
├── Dockerfile      # 필수 (ENTRYPOINT 설정)
└── exploit.py      # exploit 코드
```

### Dockerfile 규칙

**서비스:**
- `EXPOSE 4000`
- flag를 `/var/ctf/flag`에 복사
- `CMD`로 서비스 시작

**익스플로잇:**
- `ENTRYPOINT ["python3", "exploit.py"]`
- 인자: `$1` = IP, `$2` = PORT
- stdout 마지막 줄 = flag 내용
