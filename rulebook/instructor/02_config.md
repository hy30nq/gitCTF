# 강사 가이드 2: config.json 설정

## 전체 구조

```json
{
  "player": "강사 GitHub ID",
  "player_team": "instructor",
  "score_board": "스코어보드 레포 URL",
  "repo_owner": "GitHub 조직 또는 사용자",
  "intended_pts": 10,
  "unintended_pts": 100,
  "round_frequency": 600,
  "start_time": "ISO 8601 형식",
  "end_time": "ISO 8601 형식",
  "exploit_timeout": {
    "injection_phase": 10,
    "exercise_phase": 60
  },
  "teams": { ... },
  "individual": { ... }
}
```

## 필드 설명

### 기본 설정

| 필드 | 타입 | 설명 |
|------|------|------|
| `player` | string | 강사의 GitHub ID |
| `player_team` | string | `"instructor"` 고정 |
| `score_board` | string | 스코어보드 GitHub 레포 URL |
| `repo_owner` | string | 팀 레포를 소유하는 GitHub 조직 또는 사용자 |

### 점수 설정

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `intended_pts` | int | 10 | Intended 취약점 공격 시 고정 점수 |
| `unintended_pts` | int | 100 | Unintended 취약점 라운드당 누적 점수 |
| `round_frequency` | int | 600 | 점수 누적 주기 (초). 600 = 10분 |

### 시간 설정

| 필드 | 타입 | 설명 |
|------|------|------|
| `start_time` | string | 대회 시작 (ISO 8601, 예: `"2026-03-10T09:00:00+09:00"`) |
| `end_time` | string | 대회 종료 |

### 타임아웃

| 필드 | 타입 | 설명 |
|------|------|------|
| `exploit_timeout.injection_phase` | int | 주입 검증 시 exploit 타임아웃 (초) |
| `exploit_timeout.exercise_phase` | int | 공격/방어 단계 exploit 타임아웃 (초) |

### 팀 설정

```json
"teams": {
  "alpha": {
    "repo_name": "gitctf-team-alpha",
    "pub_key_id": "GPG 키 ID",
    "bug1": "커밋 해시",
    "bug2": "커밋 해시"
  },
  "instructor": {
    "repo_name": "-",
    "pub_key_id": "강사 GPG 키 ID"
  }
}
```

- `repo_name`: 팀의 GitHub 레포 이름
- `pub_key_id`: 팀의 GPG 공개키 ID
- `bug1`, `bug2`, ...: 주입 단계 후 기록하는 커밋 해시
- instructor의 `repo_name`은 반드시 `"-"`

### 개인 설정

```json
"individual": {
  "github-id": {
    "pub_key_id": "개인 GPG 키 ID",
    "team": "소속 팀명"
  }
}
```

## 예시 (6팀, 21명)

```json
{
  "player": "professor",
  "player_team": "instructor",
  "score_board": "https://github.com/IS521/scoreboard",
  "repo_owner": "IS521",
  "intended_pts": 10,
  "unintended_pts": 100,
  "round_frequency": 600,
  "start_time": "2026-05-28T09:00:00+09:00",
  "end_time": "2026-06-11T00:00:00+09:00",
  "exploit_timeout": {
    "injection_phase": 10,
    "exercise_phase": 60
  },
  "teams": {
    "team1": { "repo_name": "2026s-gitctf-team1", "pub_key_id": "AAAA1111", "bug1": "", "bug2": "" },
    "team2": { "repo_name": "2026s-gitctf-team2", "pub_key_id": "BBBB2222", "bug1": "", "bug2": "" },
    "instructor": { "repo_name": "-", "pub_key_id": "48EA8545" }
  },
  "individual": {
    "student1": { "pub_key_id": "CCCC3333", "team": "team1" },
    "student2": { "pub_key_id": "DDDD4444", "team": "team1" }
  }
}
```
