# 강사 가이드 3: 채점 시스템

## 채점 방식 개요

Git-based CTF의 채점은 **완전 자동**입니다.

1. 학생이 GitHub Issue로 exploit 제출
2. 채점기가 Notification 감지
3. Docker 환경에서 exploit 검증
4. 결과를 score.csv에 기록 + GitHub에 push

## 채점 실행

### Docker Compose (권장)
```bash
# .env에 GITHUB_TOKEN 설정 후
docker compose up -d

# 로그 확인
docker compose logs -f grader
```

### 로컬 CLI
```bash
# 연속 폴링 모드
python3 gitctf.py eval --conf config.json

# 원샷 스캔 모드 (열린 이슈 직접 처리)
python3 gitctf.py eval --scan --conf config.json
```

## 판별 알고리즘

논문 Section 3.3에 따라 exploit을 모든 서비스 버전에 대해 테스트합니다.

```
p  = 원본 프로그램 (master 브랜치)
p1 = bug1 브랜치 (첫 번째 의도된 취약점)
p2 = bug2 브랜치 (두 번째 의도된 취약점)
...
pk = bugk 브랜치 (k번째 의도된 취약점)
```

### 판별 규칙

| 조건 | 결과 | 점수 |
|------|------|------|
| pi에서만 성공 | INTENDED (vi 공격) | `intended_pts` (고정) |
| p에서만 성공 | UNINTENDED | `unintended_pts` (누적) |
| p + pi 모두 성공 | UNINTENDED | `unintended_pts` (누적) |
| 여러 pi에서 성공 | INTENDED (첫 번째) | `intended_pts` (고정) |
| 모두 실패 | FAILED | 0 |

## 방어 메커니즘 (Unintended)

Unintended 취약점이 발견되면:

1. 첫 발견 시 `unintended_pts`만큼 점수 부여
2. 이후 `round_frequency`초마다 점수 누적
3. 방어자가 master에 패치 push
4. 채점기가 새 커밋에 대해 exploit 재실행
5. exploit 실패 → 방어 성공 (점수 0 기록, "defended" 라벨)
6. exploit 성공 → 점수 계속 부여

## GitHub Label 관리

채점기가 자동으로 관리하는 라벨:

| 라벨 | 색상 | 의미 |
|------|------|------|
| `eval` | 빨강 | 채점 진행 중 |
| `verified` | 보라 | 검증 완료 |
| `failed` | 회색 | 검증 실패 |
| `intended` | 초록 | Intended 취약점 |
| `unintended` | 주황 | Unintended 취약점 |
| `defended` | 파랑 | 방어 성공 |

## 스코어보드

```bash
python3 gitctf.py score --conf config.json
```

- GitHub에서 `score.csv` 다운로드
- 점수 계산 (intended 고정 + unintended 누적)
- `score.html` 생성 (시간별 그래프)

## 트러블슈팅

### 채점기가 이슈를 감지하지 못함
- `GITHUB_TOKEN`이 올바른지 확인
- Notification 설정에서 해당 레포의 watching이 활성화되어 있는지 확인
- `--scan` 모드로 직접 처리 시도

### exploit 검증 실패
- 서비스가 Docker에서 정상 빌드되는지 확인
- exploit이 flag를 stdout 마지막 줄에 출력하는지 확인
- 타임아웃 설정이 충분한지 확인

### git push 실패 (grader 컨테이너)
- `.env`의 `GITHUB_TOKEN`에 `repo` 권한이 있는지 확인
- scoreboard 레포가 존재하는지 확인
