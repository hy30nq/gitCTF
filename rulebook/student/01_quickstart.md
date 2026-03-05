# 학생 가이드 1: 빠른 시작

## 사전 준비

### 1. 필수 소프트웨어 설치
- **Python 3.11+**: https://www.python.org/downloads/
- **Docker**: https://www.docker.com/get-started/
- **Git**: https://git-scm.com/downloads
- **GPG**: https://gnupg.org/download/

### 2. GitHub Personal Access Token 발급
1. https://github.com/settings/tokens/new 접속
2. Note: `gitctf` 입력
3. 권한 선택: `repo` (전체), `notifications`
4. Generate token → 복사해서 안전하게 보관

### 3. GPG 키 생성
```bash
gpg --full-generate-key
# 1) RSA and RSA 선택
# 2) 4096 입력
# 3) 이름, 이메일, 비밀번호 입력

# 키 ID 확인
gpg --list-keys --keyid-format short
# pub   rsa4096/ABCD1234 ← 이 ID를 강사에게 전달
```

### 4. 프로젝트 클론
```bash
git clone https://github.com/hy30nq/gitCTF.git
cd gitCTF
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_your_token_here
```

## 대회 진행

### Phase 1: 서비스 준비

팀 레포에 서비스 코드 + Dockerfile을 push합니다.

```
my-service/
├── Dockerfile       # Docker 빌드 파일
├── flag             # 기본 flag 파일
└── service.py       # 서비스 코드 (또는 server.py)
```

**중요**: flag는 `/var/ctf/flag`에 위치해야 합니다.

```bash
# 서비스 검증
python3 gitctf.py verify-service --team my-team --branch master
```

### Phase 2: 취약점 주입

1. bug 브랜치 생성 (bug1, bug2, ...)
2. 각 브랜치에 취약점 주입
3. 해당 취약점을 공격하는 exploit 작성
4. exploit을 GPG로 암호화하여 레포에 커밋

```bash
# 주입 검증 (강사가 실행)
python3 gitctf.py verify-injection --team my-team
```

### Phase 3: 공격과 방어

**공격하기:**
```bash
# 1. 상대 팀 서비스 분석 (레포 공개 후)
git clone https://github.com/org/target-team-repo.git

# 2. exploit 작성 (templates/skeletons/exploit/ 참고)

# 3. 로컬 검증
python3 gitctf.py verify-exploit \
  --exploit ./my-exploit/ \
  --service-dir ./target-team-repo/ \
  --branch bug1 --timeout 60

# 4. 제출
python3 gitctf.py submit \
  --exploit ./my-exploit/ \
  --service-dir ./target-team-repo/ \
  --branch bug1 --target target-team
```

**방어하기:**
- 자신의 레포 master 브랜치에 패치 push
- Unintended 취약점이 발견되면 빨리 수정!

**점수 확인:**
```bash
python3 gitctf.py score
# → score.html 파일 생성
```

## 점수 체계

| 유형 | 점수 | 설명 |
|------|------|------|
| Intended | 고정 (기본 10점) | 특정 bug 브랜치 취약점 공격 |
| Unintended | 누적 (기본 100점/라운드) | master 취약점 공격, 방어 시까지 누적 |
