# 강사 가이드 1: 환경 설정

## 사전 준비

1. **GitHub 계정** + Personal Access Token (PAT)
   - https://github.com/settings/tokens/new
   - 필요 권한: `repo`, `notifications`, `admin:org` (조직 사용 시)

2. **GPG 키 페어 생성**
   ```bash
   gpg --full-generate-key
   # RSA, 4096bit 권장
   gpg --list-keys  # 키 ID 확인
   ```

3. **config.json 작성**
   ```json
   {
     "player": "your-github-id",
     "player_team": "instructor",
     "score_board": "https://github.com/your-org/scoreboard",
     "repo_owner": "your-org",
     "intended_pts": 10,
     "unintended_pts": 100,
     "round_frequency": 600,
     "start_time": "2026-03-10T09:00:00+09:00",
     "end_time": "2026-03-24T18:00:00+09:00",
     "exploit_timeout": {
       "injection_phase": 10,
       "exercise_phase": 60
     },
     "teams": { ... },
     "individual": { ... }
   }
   ```

## 환경 설정

### 방법 1: Docker Compose (권장)

```bash
git clone https://github.com/hy30nq/gitCTF.git
cd gitCTF
cp .env.example .env
# .env에 GITHUB_TOKEN 입력
docker compose up -d
```

- 웹 대시보드: http://localhost:8080
- 자동 채점기가 백그라운드에서 실행됨

### 방법 2: 로컬 CLI

```bash
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx

# GitHub 레포 생성
python3 gitctf.py setup --conf config.json

# 자동 채점 시작
python3 gitctf.py eval --conf config.json
```

## 대회 진행 순서

### 1단계: 환경 초기화
```bash
python3 gitctf.py setup --conf config.json
```
- 각 팀의 GitHub 레포 생성 (private)
- 팀원을 collaborator로 추가 (수동)

### 2단계: 준비 단계 (Preparation)
- 각 팀이 서비스 + Dockerfile 준비
- 강사가 서비스 검증:
  ```bash
  python3 gitctf.py verify-service --team alpha --branch master
  ```

### 3단계: 주입 단계 (Injection)
- 각 팀이 bug 브랜치에 취약점 주입 + 암호화된 exploit 커밋
- 강사가 주입 검증:
  ```bash
  python3 gitctf.py verify-injection --team alpha
  ```
- 커밋 해시 기록:
  ```bash
  python3 gitctf.py hash --conf config.json
  ```
  → config.json의 `bug1`, `bug2` 등에 해시 입력

### 4단계: 공격/방어 단계 (Exercise)
- 레포를 public으로 전환
- 자동 채점 시작:
  ```bash
  python3 gitctf.py eval --conf config.json
  # 또는 docker compose up -d (grader 서비스)
  ```

### 5단계: 결과 확인
```bash
python3 gitctf.py score --conf config.json
# → score.html 생성
```

## 주의사항

- `config.json`에 instructor의 `repo_name`은 `"-"`로 설정
- GPG 공개키를 모든 팀과 공유해야 함
- 대회 시간(`start_time`, `end_time`)을 정확히 설정
- `round_frequency`는 unintended 점수 누적 주기 (초 단위)
