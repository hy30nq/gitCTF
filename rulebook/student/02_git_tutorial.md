# 참가자 가이드 — 2. Git 기초 튜토리얼

## Git이란?

버전 관리 시스템입니다. 코드의 변경 이력을 추적하고, 여러 사람이 협업할 수 있게 해줍니다.

## 필수 명령어

### 레포지토리 클론
```bash
git clone git@github.com:ORG/repo-name.git
cd repo-name
```

### 브랜치 관리
```bash
# 현재 브랜치 확인
git branch

# 새 브랜치 생성 & 이동
git checkout -b bug1

# 브랜치 이동
git checkout master

# 원격 브랜치 목록
git branch -r
```

### 변경사항 커밋
```bash
# 변경된 파일 확인
git status

# 모든 파일 스테이징
git add .

# 커밋
git commit -m "bug1: add vulnerability"

# 원격에 푸시
git push origin bug1
```

### 변경사항 가져오기
```bash
# 최신 코드 가져오기
git pull origin master
```

## GitCTF에서의 Git 사용

### 서비스 개발 (master 브랜치)
```bash
git checkout master
# 서비스 코드 개발...
git add .
git commit -m "feat: add authentication"
git push origin master
```

### 취약점 주입 (bug 브랜치)
```bash
git checkout -b bug1
# 취약점 코드 추가...
git add .
git commit -m "bug1: add SQL injection"
git push origin bug1
```

## 주의사항

- **master 브랜치에는 취약점을 넣지 마세요** (정상 서비스만!)
- bug 브랜치에서만 취약점이 동작해야 합니다
- 커밋 메시지를 명확하게 작성하세요
