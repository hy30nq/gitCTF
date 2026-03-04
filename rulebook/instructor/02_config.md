# 관리자 가이드 — 2. config.json 설정

## 파일 구조

```json
{
    "player": "admin-github-id",
    "player_team": "instructor",
    "score_board": "https://github.com/ORG/scoreboard",
    "repo_owner": "ORG",
    "intended_pts": 10,
    "unintended_pts": 100,
    "round_frequency": 600,
    "start_time": "2026-05-01T09:00:00+09:00",
    "end_time": "2026-05-15T18:00:00+09:00",
    "exploit_timeout": {
        "injection_phase": 10,
        "exercise_phase": 60
    },
    "teams": {
        "team1": {
            "repo_name": "gitctf-team1",
            "pub_key_id": "AAAAAAAA",
            "bug1": "commit_hash",
            "bug2": "commit_hash"
        },
        "instructor": {
            "repo_name": "-",
            "pub_key_id": "INSTRUCTOR_KEY"
        }
    },
    "individual": {
        "github_id": {
            "pub_key_id": "XXXXXXXX",
            "team": "team1"
        }
    }
}
```

## 필드 설명

| 필드 | 설명 |
|------|------|
| `player` | 현재 사용자의 GitHub ID |
| `player_team` | 현재 사용자의 팀명 |
| `score_board` | 점수판 GitHub 저장소 URL |
| `repo_owner` | GitHub 조직 또는 사용자명 |
| `intended_pts` | 의도된 취약점 공격 점수 |
| `unintended_pts` | 비의도된 취약점 공격 점수 (라운드당) |
| `round_frequency` | 라운드 주기 (초) |
| `start_time` / `end_time` | 대회 시작/종료 시각 (ISO 8601) |
| `exploit_timeout` | 익스플로잇 실행 제한 시간 (초) |
| `teams.*.repo_name` | 팀의 GitHub 저장소명 |
| `teams.*.pub_key_id` | 팀의 GPG 공개키 ID |
| `teams.*.bugN` | N번째 취약점 브랜치의 커밋 해시 |
| `individual.*.pub_key_id` | 개인 참가자의 GPG 키 ID |
| `individual.*.team` | 소속 팀명 |

## 점수 체계

- **의도된 취약점**: 공격 성공 시 `intended_pts` 점 (1회)
- **비의도된 취약점**: `round_frequency`초마다 `unintended_pts`점 누적 (방어팀이 패치할 때까지)
- **자기 팀 공격**: 불가
