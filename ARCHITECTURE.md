# Git-based CTF v2.0 — 아키텍처 문서

## 1. 시스템 개요

Git-based CTF는 **서버리스** 아키텍처입니다. 모든 데이터는 GitHub에 저장되며, 별도 데이터베이스나 API 서버가 없습니다.

```
┌─────────────────────────────────────────────────────────┐
│                      GitHub                              │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ Team Repos  │  │ Team Repos  │  │ Scoreboard Repo │ │
│  │ (서비스 코드, │  │ (서비스 코드, │  │ (score.csv)     │ │
│  │  bug 브랜치, │  │  bug 브랜치, │  │                 │ │
│  │  Issues)    │  │  Issues)    │  │                 │ │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘ │
│         │                │                   │          │
│         └────────────────┼───────────────────┘          │
│                          │                              │
│              GitHub REST API v3                          │
│              + Notifications API                         │
└──────────────────────────┬──────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐   ┌───────────┐   ┌────────────────┐
    │ 참가자 PC  │   │ 참가자 PC  │   │ 강사 환경       │
    │           │   │           │   │                │
    │ gitctf.py │   │ gitctf.py │   │ docker compose │
    │ Docker    │   │ Docker    │   │  ├─ web        │
    │ GPG       │   │ GPG       │   │  ├─ grader     │
    │           │   │           │   │  └─ dind       │
    └───────────┘   └───────────┘   └────────────────┘
```

## 2. 데이터 흐름

### 2.1 공격 제출 흐름
```
참가자 → verify-exploit (로컬 Docker 검증)
       → GPG 암호화 (instructor + target team 공개키)
       → GitHub Issue 생성 (target team repo)
```

### 2.2 자동 채점 흐름
```
grader → GitHub Notifications API 폴링
       → 새 Issue 발견
       → git clone (target repo)
       → GPG 복호화 (exploit)
       → 각 bug 브랜치(p1~pk) + master(p)에 대해:
           → docker build (서비스)
           → docker run (서비스, 랜덤 flag 주입)
           → docker build (exploit)
           → docker run (exploit)
           → flag 비교
       → Intended/Unintended 판별
       → score.csv에 기록
       → git push (scoreboard repo)
       → GitHub Issue에 결과 코멘트 + 라벨 + 닫기
```

### 2.3 방어 검증 흐름 (Unintended)
```
grader → 이전 공격 기록 조회 (score.csv)
       → 방어자의 이후 커밋 순회
       → 각 커밋에 대해 exploit 재실행
       → exploit 실패 → 방어 성공 (pts=0 기록, "defended" 라벨)
       → exploit 성공 → 점수 계속 부여
```

## 3. 모듈 의존성

```
gitctf.py (CLI 진입점)
├── lib/verify_service.py    → git.py, utils.py
├── lib/verify_exploit.py    → git.py, utils.py, crypto.py
├── lib/verify_injection.py  → git.py, verify_exploit.py, crypto.py
├── lib/submit.py            → verify_exploit.py, crypto.py, issue.py
├── lib/fetch.py             → issue.py, crypto.py
├── lib/show_score.py        → github_api.py, utils.py
├── lib/evaluate.py          → verify_issue.py, issue.py, git.py
│   └── lib/verify_issue.py  → verify_exploit.py, crypto.py, git.py
├── lib/get_hash.py          → github_api.py
├── lib/setup_env.py         → github_api.py
└── lib/execute.py           → utils.py
```

## 4. Docker Compose 아키텍처

### 4.1 서비스 구성
```yaml
services:
  web:        # Nginx + 정적 HTML (GitHub API 직접 호출)
  grader:     # Python 3.11 + docker-ce-cli (eval 루프)
  dind:       # Docker-in-Docker (grader용 Docker 데몬)
```

### 4.2 네트워크
- 3개 서비스는 Docker Compose 기본 네트워크(`gitctf_default`)로 연결
- grader → dind: `DOCKER_HOST=tcp://dind:2375`
- web: 호스트 포트 8080 → 컨테이너 포트 80

### 4.3 데이터 저장
- **영구 데이터 없음**: 모든 데이터는 GitHub에 저장
- `config.json`: 읽기 전용 볼륨으로 마운트
- `.score/`: grader가 실행 시 clone, 작업 후 push

## 5. 보안 모델

### 5.1 Exploit 보호
- GPG 암호화: instructor + target team 공개키로 암호화
- GitHub Issue body에 암호문 저장
- 복호화는 instructor 또는 해당 팀만 가능

### 5.2 인증
- GitHub PAT (Personal Access Token)
- 환경변수 `GITHUB_TOKEN` 또는 `--token` 옵션
- 웹 대시보드: 브라우저 localStorage에만 저장 (서버 전송 없음)

### 5.3 자기 팀 공격 차단
- `evaluate.py`에서 `config["individual"][attacker]["team"] == defender` 체크
- 자기 팀 공격 시 "failed" 라벨 + 이슈 닫기

## 6. 점수 저장 형식

### score.csv
```
timestamp,attacker,defender,branch,bugkind,points
1709528400,alice,beta,bug1,abc123...,10
1709528500,bob,alpha,unintended,def456...,100
1709529000,alpha,unintended,bob,ghi789...,0
```

| 필드 | 설명 |
|------|------|
| timestamp | Unix timestamp |
| attacker | 공격자 GitHub ID |
| defender | 방어 팀명 |
| branch | 취약점 유형 (bug1, bug2, ... 또는 "unintended") |
| bugkind | 커밋 해시 |
| points | 점수 (0 = 방어 기록) |
