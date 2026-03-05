# Git-based CTF v2.0

**완전 분산형, 서버리스 Attack-and-Defense CTF 프레임워크**

모든 데이터는 GitHub에 저장됩니다. 별도 서버가 필요 없습니다.  
`docker compose up` 한 번으로 관리 환경이 세팅됩니다.

> 원본 논문: [Git-based CTF (ASE 2018, KAIST SoftSec Lab)](ase18-paper_wi.pdf)

---

## 핵심 원칙

> "Instructors in Git-based CTF **do not have to prepare a separate server** to run a CTF."

- **GitHub = 유일한 데이터 소스**: 레포지토리, 이슈, 알림, score.csv
- **Docker = 로컬 전용**: 참가자/강사 각자의 머신에서 서비스·익스플로잇 실행
- **CLI 도구**: `gitctf.py`로 모든 작업 수행
- **GPG 암호화**: 익스플로잇은 PGP로 암호화 후 GitHub Issue로 제출

---

## 빠른 시작

### 방법 1: Docker Compose (권장)

```bash
git clone https://github.com/hy30nq/gitCTF.git
cd gitCTF
cp .env.example .env        # GITHUB_TOKEN 설정
vi .env                      # 토큰 입력
docker compose up -d         # 끝!
```

- 웹 대시보드: http://localhost:8080
- 자동 채점기: 백그라운드에서 GitHub 폴링 중
- 모든 데이터는 GitHub에서 가져옴 (DB 없음)

### 방법 2: 로컬 CLI

```bash
git clone https://github.com/hy30nq/gitCTF.git
cd gitCTF
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_your_token_here
python3 gitctf.py --help
```

---

## Docker Compose 구성

| 서비스 | 역할 | 포트 |
|--------|------|------|
| **web** | Nginx 대시보드 (GitHub API로 데이터 fetch) | 8080 |
| **grader** | 자동 채점기 (GitHub Notification poll → Docker 검증 → score push) | - |
| **dind** | Docker-in-Docker (grader가 서비스/익스플로잇 컨테이너 실행) | - |

```
┌─────────────────────────────────────────────┐
│                  GitHub                      │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Team1    │ │ Team2    │ │ Scoreboard │  │
│  │ Repo     │ │ Repo     │ │ (score.csv)│  │
│  └──────────┘ └──────────┘ └────────────┘  │
└──────────────────┬──────────────────────────┘
                   │ GitHub API
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────────────┐
│ Student  │ │ Student  │ │ docker compose   │
│ Machine  │ │ Machine  │ │ ┌──────────────┐ │
│          │ │          │ │ │ web (Nginx)  │ │
│ gitctf   │ │ gitctf   │ │ │ grader (eval)│ │
│ Docker   │ │ Docker   │ │ │ dind (Docker)│ │
│ GPG      │ │ GPG      │ │ └──────────────┘ │
└──────────┘ └──────────┘ └──────────────────┘
```

---

## 대회 워크플로우

### Phase 1: 준비 (Preparation)
각 팀이 네트워크 서비스 + Dockerfile을 준비합니다.

```bash
# 서비스 빌드/실행 검증
python3 gitctf.py verify-service --team alpha --branch master
```

### Phase 2: 취약점 주입 (Injection)
각 팀이 N개의 취약점을 별도 브랜치(bug1, bug2, ...)에 주입합니다.

```bash
# 주입 검증 (exploit 복호화 → bug 브랜치 테스트 → master 테스트)
python3 gitctf.py verify-injection --team alpha

# 자체 익스플로잇 검증
python3 gitctf.py verify-exploit \
  --exploit ./my-exploit/ \
  --service-dir ./service/ \
  --branch bug1 --timeout 60
```

### Phase 3: 공격과 방어 (Exercise)

**공격:**
```bash
# 1. 로컬에서 익스플로잇 검증
python3 gitctf.py verify-exploit \
  --exploit ./exploit/ --service-dir ./target/ \
  --branch bug1 --timeout 60

# 2. 암호화 후 GitHub Issue로 제출
python3 gitctf.py submit \
  --exploit ./exploit/ --service-dir ./target/ \
  --branch bug1 --target alpha
```

**방어:** master 브랜치에 패치를 push합니다.

**점수 확인:**
```bash
python3 gitctf.py score
# → score.html 생성 (시간별 점수 그래프)
```

---

## 강사 명령어

```bash
# 환경 초기 설정 (GitHub 레포 생성)
python3 gitctf.py setup --conf config.json

# 자동 채점 시작 (GitHub Notification 폴링)
python3 gitctf.py eval --conf config.json

# 원샷 스캔 모드 (열린 이슈 직접 처리)
python3 gitctf.py eval --scan --conf config.json

# 커밋 해시 확인
python3 gitctf.py hash --conf config.json
```

---

## 점수 체계

논문 Section 3.3에 따른 자동 채점:

1. **Intended 취약점**: 고정 점수 (`intended_pts`, 기본 10점)
   - exploit이 특정 bug 브랜치에서만 동작 → 해당 취약점 공격으로 인정
2. **Unintended 취약점**: 시간 누적 점수 (`unintended_pts`, 기본 100점)
   - exploit이 master에서 동작 → unintended로 분류
   - `round_frequency`초마다 점수 누적
   - 방어자가 패치하면 누적 중단

### 판별 알고리즘
```
p = 원본 프로그램 (master)
p1, p2, ..., pk = 취약점 주입 버전 (bug1, bug2, ...)

exploit을 p1~pk와 p에 대해 실행:
  - 특정 pi에서만 성공 → INTENDED (vi 공격)
  - p에서만 성공 → UNINTENDED
  - p + pi 모두 성공 → UNINTENDED
  - 모두 실패 → 실패 (점수 없음)
```

---

## 전체 CLI 명령어

| 명령어 | 대상 | 설명 |
|--------|------|------|
| `verify-service` | 참가자 | 서비스 Docker 빌드/실행 검증 |
| `verify-exploit` | 참가자 | 익스플로잇 로컬 검증 |
| `verify-injection` | 강사 | 취약점 주입 검증 (exploit 복호화+실행) |
| `submit` | 참가자 | 암호화된 익스플로잇을 GitHub Issue로 제출 |
| `fetch` | 참가자/강사 | GitHub Issue에서 익스플로잇 다운로드/복호화 |
| `score` | 모두 | GitHub에서 score.csv fetch → HTML 스코어보드 |
| `eval` | 강사 | 자동 채점 (Notification poll → Docker 검증) |
| `hash` | 강사 | 팀별 브랜치 커밋 해시 조회 |
| `setup` | 강사 | GitHub 레포 생성 등 환경 초기화 |
| `exec-service` | 참가자 | 서비스 로컬 Docker 실행 |
| `exec-exploit` | 참가자 | 익스플로잇 로컬 Docker 실행 |

---

## 프로젝트 구조

```
GitCTF/
├── gitctf.py              # CLI 진입점 (11개 명령어)
├── config.json            # 대회 설정
├── docker-compose.yml     # 원커맨드 실행 (web + grader + dind)
├── .env.example           # 환경변수 템플릿
├── requirements.txt       # Python 의존성
├── docker/                # Docker 빌드 파일
│   ├── web.Dockerfile     # Nginx 대시보드
│   ├── grader.Dockerfile  # 자동 채점기
│   ├── nginx.conf         # Nginx 설정
│   └── entrypoint-grader.sh
├── lib/                   # 핵심 모듈 (16개)
│   ├── github_api.py      # GitHub API 클라이언트
│   ├── git.py             # Git 명령어 래퍼
│   ├── crypto.py          # GPG 암호화/복호화
│   ├── issue.py           # GitHub Issue 조작
│   ├── evaluate.py        # 자동 채점 + 방어 검증
│   ├── verify_issue.py    # Intended/Unintended 판별
│   ├── verify_exploit.py  # Docker 기반 exploit 검증
│   ├── verify_service.py  # 서비스 빌드/실행 검증
│   ├── verify_injection.py# 취약점 주입 검증
│   ├── submit.py          # 익스플로잇 제출
│   ├── fetch.py           # 익스플로잇 다운로드
│   ├── show_score.py      # 스코어보드 생성
│   ├── execute.py         # 로컬 Docker 실행
│   ├── get_hash.py        # 브랜치 해시 조회
│   ├── setup_env.py       # 환경 초기화
│   └── utils.py           # 공통 유틸리티
├── docs/
│   └── index.html         # 웹 대시보드 (정적 HTML)
├── templates/
│   ├── score.template     # 스코어보드 HTML 템플릿
│   └── skeletons/         # 스켈레톤 코드
│       ├── exploit/       # 익스플로잇 템플릿
│       ├── system/        # 시스템 서비스 템플릿
│       └── web/           # 웹 서비스 템플릿
├── rulebook/              # 대회 가이드
│   ├── instructor/        # 강사용
│   └── student/           # 학생용
└── _legacy/               # 원본 Python 2 구현
```

---

## 라이선스

Apache License 2.0

## 인용

```bibtex
@inproceedings{gitctf2018,
  title={Git-based CTF: A Simple and Effective Approach to Organizing
         In-Course Attack-and-Defense Security Competition},
  author={Wi, SeongIl and Choi, Jaeseung and Cha, Sang Kil},
  booktitle={ASE 2018},
  year={2018}
}
```
