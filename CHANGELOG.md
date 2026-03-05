# Changelog

## v2.0.0 (2026-03-04)

v1.0 (Python 2, KAIST SoftSec Lab 2018) 기반 전면 재작성.

### 추가
- **Docker Compose 지원**: `docker compose up -d`로 웹 대시보드 + 자동 채점기 + DinD 일괄 실행
- **웹 대시보드** (`docs/index.html`): GitHub API 기반 정적 HTML, 스코어보드/팀/공격 현황/토큰 설정
- **Intended vs Unintended 자동 판별**: 논문 알고리즘 정확 구현 (p1~pk + p 전체 테스트)
- **방어 메커니즘** (`process_unintended`): 패치 커밋 순회 → exploit 재실행 → "defended" 라벨
- **스캔 모드** (`eval --scan`): Notification 없이 열린 이슈 직접 처리
- **서비스 스켈레톤**: system(socat), web(Flask), exploit 3종 제공
- **룰북**: 강사용 2편 (setup, config) + 학생용 4편 (quickstart, git, docker, gpg)
- **GitHub Label 자동 관리**: eval/verified/failed/defended/intended/unintended
- **.env.example**: 환경변수 템플릿
- **score.template**: HTML 스코어보드 그래프 템플릿

### 변경
- **Python 2 → 3.11+**: 전체 코드 재작성
- **requests → httpx**: 모던 HTTP 클라이언트
- **CLI**: 수동 파싱 → argparse 서브커맨드 (11개)
- **timeout**: bash `timeout` → Python `subprocess.timeout` + Docker `--stop-timeout` (macOS 호환)
- **flag 경로**: 설정 가능 → `/var/ctf/flag` 고정 (논문 준수)
- **git clone**: SSH 우선 → GITHUB_TOKEN 기반 HTTPS 우선 (자동화 호환)
- **verify_injection**: 브랜치 존재 확인만 → 실제 exploit 복호화+실행 검증
- **show_score**: intended 점수 즉시 반영, unintended 시간 누적 분리

### 수정
- macOS에서 `timeout` 명령 없음 → 크로스 플랫폼 호환
- grader 컨테이너 Docker CLI 누락 → docker-ce-cli 설치
- grader git push 인증 실패 → credential helper 자동 설정
- Python stdout 버퍼링 → PYTHONUNBUFFERED=1
- Label 중복 생성 에러 → post_quiet 사용
- 자기 팀 공격 시 KeyError → .get() 안전 접근
- repo_name이 "-"인 instructor 항목 처리

### 제거
- bash 스크립트 의존성 (`setup_service.sh`, `launch_exploit.sh`, `cleanup.sh`)
- Python 2 전용 코드 (`print` 문, `StringIO`, `reload(sys)`)
- `.config.json` (admin 설정 → `config.json`으로 통합)

---

## v1.0.0 (2018)

KAIST SoftSec Lab 원본 릴리스.
- Python 2.7
- bash 스크립트 기반 Docker 실행
- GitHub API v3 (requests)
- GPG 암호화
