# 관리자 가이드 — 1. 환경 설정

## 사전 요구사항

- Python 3.11+
- Docker Desktop
- Git
- GPG
- GitHub 조직(Organization) 또는 개인 계정
- GitHub Personal Access Token (`repo`, `notifications` 권한)

## 빠른 시작

```bash
# 1. 프로젝트 클론
git clone https://github.com/YOUR_ORG/GitCTF.git
cd GitCTF

# 2. Python 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
export GITHUB_TOKEN=ghp_your_token_here

# 4. config.json 편집
# 팀 정보, 저장소명, GPG 키 ID 등을 설정

# 5. CTF 환경 구축 (GitHub 저장소 생성)
python gitctf.py setup --admin-conf .config.json --token $GITHUB_TOKEN
```

## 핵심 원칙

**서버가 필요 없습니다.** 모든 데이터는 GitHub에 저장됩니다.

- 서비스 코드 → 각 팀의 GitHub 저장소
- 공격 제출 → GitHub Issue (GPG 암호화)
- 점수판 → 별도의 GitHub 저장소에 score.csv로 저장
- 채점 → 관리자가 자신의 머신에서 `gitctf eval` 실행

## 채점 시작

```bash
# 자동 채점 루프 시작 (GitHub Notification 폴링)
python gitctf.py eval --conf config.json --token $GITHUB_TOKEN
```

이 스크립트는:
1. GitHub Notification에서 새 Issue(공격 제출)를 감지
2. 대상 서비스를 로컬 Docker에서 빌드/실행
3. 제출된 익스플로잇을 복호화 후 Docker에서 실행
4. 플래그 일치 여부 확인
5. 결과를 score.csv에 기록, GitHub에 푸시

## 점수 확인

```bash
python gitctf.py score --conf config.json
# → 터미널에 현재 점수 출력
# → score.html 파일 생성 (시간별 그래프)
```
