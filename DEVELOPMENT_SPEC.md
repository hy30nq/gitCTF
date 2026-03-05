# Git-based CTF v2.0 — 개발 명세서

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | Git-based CTF v2.0 |
| 원본 | KAIST SoftSec Lab (ASE 2018) |
| 목적 | 수업 내 Attack-and-Defense CTF를 최소 비용으로 운영 |
| 핵심 철학 | 서버리스, GitHub 중심, 완전 분산 |
| 언어 | Python 3.11+ |
| 실행 방식 | `docker compose up` 또는 로컬 CLI |

## 2. 원본(v1.0) 대비 변경 사항

### 2.1 언어 및 런타임
| 항목 | v1.0 | v2.0 |
|------|------|------|
| Python | 2.7 | 3.11+ |
| HTTP 클라이언트 | requests | httpx |
| 타입 힌트 | 없음 | 전체 적용 |
| 패키지 관리 | 없음 | requirements.txt |

### 2.2 아키텍처
| 항목 | v1.0 | v2.0 |
|------|------|------|
| 실행 방식 | 로컬 스크립트만 | Docker Compose + 로컬 CLI |
| 웹 대시보드 | 없음 | Nginx + 정적 HTML (GitHub API) |
| 자동 채점 | 로컬 스크립트 | Docker 컨테이너 (grader) |
| Docker 실행 | 호스트 직접 | Docker-in-Docker (dind) |
| timeout | bash `timeout` 명령 | Python `subprocess.timeout` + Docker `--stop-timeout` |

### 2.3 기능
| 항목 | v1.0 | v2.0 |
|------|------|------|
| CLI 구조 | 수동 파싱 | argparse 서브커맨드 |
| 스캔 모드 | 없음 | `eval --scan` (원샷 이슈 처리) |
| 토큰 관리 | 명령줄만 | 환경변수 + 명령줄 + 웹 GUI |
| 스켈레톤 코드 | 바이너리 예제만 | system/web/exploit 3종 |
| 룰북 | 없음 | 강사용 2편 + 학생용 4편 |
| flag 경로 | 설정 가능 | `/var/ctf/flag` 고정 (논문 준수) |
| 점수 판별 | 단일 브랜치 테스트 | 전체 bug 브랜치 + master 테스트 |
| 방어 메커니즘 | 커밋 순회 검증 | 동일 구현 + "defended" 라벨 |

## 3. 구현된 모듈 상세

### 3.1 CLI 명령어 (11개)

| 명령어 | 모듈 | 논문 섹션 | 설명 |
|--------|------|-----------|------|
| `verify-service` | `verify_service.py` | 3.1 | 서비스 Docker 빌드/실행 검증 |
| `verify-exploit` | `verify_exploit.py` | 3.2 | 랜덤 flag 주입 후 exploit 실행 검증 |
| `verify-injection` | `verify_injection.py` | 3.2 | 암호화 exploit 복호화 → bug/master 교차 검증 |
| `submit` | `submit.py` | 3.3 | 로컬 검증 → GPG 암호화 → GitHub Issue 생성 |
| `fetch` | `fetch.py` | 3.3 | GitHub Issue에서 exploit 다운로드/복호화 |
| `score` | `show_score.py` | 3.3 | score.csv fetch → 점수 계산 → HTML 생성 |
| `eval` | `evaluate.py` | 3.3 | Notification poll → Docker 검증 → score push |
| `hash` | `get_hash.py` | 3.2 | 팀별 브랜치 커밋 해시 조회 |
| `setup` | `setup_env.py` | 3.0 | GitHub 레포 생성 |
| `exec-service` | `execute.py` | - | 서비스 로컬 실행 |
| `exec-exploit` | `execute.py` | - | 익스플로잇 로컬 실행 |

### 3.2 핵심 라이브러리 (6개)

| 모듈 | 역할 |
|------|------|
| `github_api.py` | GitHub REST API v3 클라이언트 (httpx) |
| `git.py` | git clone/checkout/branch/log 래퍼 |
| `crypto.py` | GPG 암호화/복호화 (exploit 보호) |
| `issue.py` | GitHub Issue CRUD + Label 관리 |
| `utils.py` | 공통 유틸리티 (run_command, random_string 등) |
| `verify_issue.py` | Intended/Unintended 판별 알고리즘 |

### 3.3 Docker Compose 서비스 (3개)

| 서비스 | 이미지 | 역할 |
|--------|--------|------|
| `web` | nginx:alpine | 정적 대시보드 (GitHub API 직접 호출) |
| `grader` | python:3.11-slim + docker-ce-cli | 자동 채점 루프 |
| `dind` | docker:27-dind | grader용 Docker 데몬 |

## 4. 논문 요구사항 매핑

### 4.1 Section 3.0 — Configuration
- [x] GitHub 레포 생성 (`setup`)
- [x] PGP 키 페어 관리 (`crypto.py`)
- [x] config.json으로 대회 설정
- [x] 별도 서버 불필요

### 4.2 Section 3.1 — Preparation Phase
- [x] 네트워크 서비스 + Dockerfile 준비
- [x] flag.txt → /var/ctf/ 복사 (Dockerfile 템플릿)
- [x] `git clone` → `docker build` → `docker run` 자동 검증
- [x] 서비스 스켈레톤 제공 (system, web)

### 4.3 Section 3.2 — Injection Phase
- [x] N개 bug 브랜치에 취약점 주입
- [x] 각 브랜치별 암호화된 exploit 저장
- [x] 주입 검증: exploit이 bug에서 성공, master에서 실패 확인
- [x] 커밋 해시 기록 (`hash` 명령어)

### 4.4 Section 3.3 — Exercise Phase
- [x] 레포 공개 후 공격/방어
- [x] exploit 암호화 후 GitHub Issue로 제출
- [x] 자동 채점: p1~pk + p 전체 테스트
- [x] Intended vs Unintended 자동 판별
- [x] Intended: 고정 점수 (intended_pts)
- [x] Unintended: 시간 누적 (round_frequency마다 unintended_pts)
- [x] 방어: 패치 커밋 순회 → exploit 재실행 → 방어 성공 시 누적 중단
- [x] 자기 팀 공격 차단
- [x] GitHub Label 관리 (eval/verified/failed/defended/intended/unintended)
- [x] 스코어보드: CSV → HTML 그래프

### 4.5 Section 5 — Discussion
- [x] 치팅 방지: GPG 서명으로 제출자 확인 가능
- [x] 다양한 서비스 유형 지원 (system/web 스켈레톤)

## 5. config.json 스키마

```json
{
  "player": "GitHub ID",
  "player_team": "팀명 또는 instructor",
  "score_board": "https://github.com/owner/scoreboard-repo",
  "repo_owner": "GitHub 조직 또는 사용자",
  "intended_pts": 10,
  "unintended_pts": 100,
  "round_frequency": 600,
  "start_time": "ISO 8601",
  "end_time": "ISO 8601",
  "exploit_timeout": {
    "injection_phase": 10,
    "exercise_phase": 60
  },
  "teams": {
    "team_name": {
      "repo_name": "레포명",
      "pub_key_id": "GPG 키 ID",
      "bug1": "커밋 해시",
      "bug2": "커밋 해시"
    }
  },
  "individual": {
    "github_id": {
      "pub_key_id": "GPG 키 ID",
      "team": "소속 팀"
    }
  }
}
```

## 6. 기술 스택

| 분류 | 기술 | 버전 |
|------|------|------|
| 언어 | Python | 3.11+ |
| HTTP | httpx | 0.27+ |
| 암호화 | python-gnupg | 0.5+ |
| 날짜 | python-dateutil | 2.9+ |
| 컨테이너 | Docker | 24+ |
| 오케스트레이션 | Docker Compose | v2 |
| 웹 서버 | Nginx | alpine |
| VCS | Git | 2.x |
| 플랫폼 | GitHub API | v3 |
