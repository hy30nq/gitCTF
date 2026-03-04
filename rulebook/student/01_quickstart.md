# 참가자 가이드 — 1. 빠른 시작

## 대회 진행 순서

```
1. 환경 설정 → 2. 서비스 개발 → 3. 취약점 주입 → 4. 공격 & 방어
```

## 1단계: 환경 설정

### 필수 설치
- **Python 3.11+** — `python3 --version`
- **Git** — `git --version`
- **Docker** — Docker Desktop 설치 후 `docker --version`
- **GPG** — `gpg --version`

### GitHub 토큰 발급
1. GitHub → Settings → Developer settings → Personal access tokens
2. `repo`, `notifications` 권한 체크
3. 발급된 토큰을 안전하게 보관

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### Python 의존성 설치
```bash
pip install -r requirements.txt
```

### GPG 키 생성
```bash
gpg --full-generate-key
gpg --armor --export YOUR_KEY_ID > my_public_key.asc
```

> ⚠️ **절대로 개인키(PRIVATE KEY)를 제출하지 마세요!**
> 공개키 파일은 `BEGIN PGP PUBLIC KEY BLOCK`으로 시작합니다.

## 2단계: 서비스 개발

서비스는 **Docker 컨테이너 안에서** 실행됩니다.
- `Dockerfile`이 반드시 포함
- 지정된 포트에서 네트워크 서비스 제공
- `flag` 파일을 읽어 컨테이너 내에 저장

```bash
# 서비스 빌드 & 테스트
docker build -t my-service .
docker run -p 4000:4000 my-service
```

## 3단계: 취약점 주입

별도 브랜치(bug1, bug2...)에 취약점을 주입합니다.

```bash
git checkout -b bug1
# 취약점을 코드에 주입
git add . && git commit -m "inject vulnerability"
git push origin bug1
```

각 취약점에 대한 익스플로잇을 작성하고 검증합니다:
```bash
python gitctf.py verify-exploit \
  --exploit ./my-exploit/ \
  --service-dir ./my-service/ \
  --branch bug1 --timeout 60 --encrypt \
  --conf config.json
```

## 4단계: 공격 & 방어

### 공격
```bash
# 1. 대상 서비스 클론
git clone https://github.com/ORG/target-team-repo

# 2. 익스플로잇 작성 후 로컬 검증
python gitctf.py verify-exploit \
  --exploit ./exploit/ --service-dir ./target-repo/ \
  --branch bug1 --timeout 60 --conf config.json

# 3. 암호화하여 GitHub Issue로 제출
python gitctf.py submit \
  --exploit ./exploit/ --service-dir ./target-repo/ \
  --branch bug1 --target team2 --conf config.json
```

### 방어
비의도된 취약점이 발견되면 master 브랜치에서 패치:
```bash
git checkout master
# 취약점 수정
git add . && git commit -m "fix vulnerability"
git push origin master
```

### 점수 확인
```bash
python gitctf.py score --conf config.json
```
