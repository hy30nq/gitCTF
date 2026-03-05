# 학생 가이드 3: 공격과 방어

## 공격 (Attack)

### 1단계: 상대 팀 서비스 분석

대회 Exercise Phase가 시작되면 모든 팀의 레포가 공개됩니다.

```bash
# 상대 팀 레포 클론
git clone https://github.com/org/target-team-repo.git
cd target-team-repo

# 코드 분석
cat service.py
cat Dockerfile
```

### 2단계: exploit 작성

`templates/skeletons/exploit/` 디렉토리를 참고하여 exploit을 작성합니다.

```
my-exploit/
├── Dockerfile
└── exploit.py
```

**exploit 규칙:**
- `sys.argv[1]` = 서비스 IP
- `sys.argv[2]` = 서비스 포트
- `/var/ctf/flag` 파일의 내용을 **stdout 마지막 줄**에 출력
- Dockerfile의 ENTRYPOINT에서 실행

### 3단계: 로컬 검증

```bash
python3 gitctf.py verify-exploit \
  --exploit ./my-exploit/ \
  --service-dir ./target-team-repo/ \
  --branch master \
  --timeout 60
```

이 명령은:
1. 서비스를 Docker로 빌드/실행 (랜덤 flag 주입)
2. exploit을 Docker로 빌드/실행
3. exploit 출력의 마지막 줄과 주입된 flag 비교
4. 일치하면 성공

### 4단계: 제출

```bash
python3 gitctf.py submit \
  --exploit ./my-exploit/ \
  --service-dir ./target-team-repo/ \
  --branch master \
  --target target-team
```

이 명령은:
1. 로컬에서 exploit 검증 (verify-exploit)
2. exploit 디렉토리를 zip 압축
3. GPG로 암호화 (강사 + 대상 팀 공개키)
4. 대상 팀 레포에 GitHub Issue 생성

### 5단계: 결과 확인

- 채점기가 자동으로 Issue를 처리합니다
- Issue에 결과 코멘트가 달립니다:
  - **성공**: "Verified: INTENDED/UNINTENDED vulnerability"
  - **실패**: "The exploit did not work" + 로그

## 방어 (Defense)

### Unintended 취약점 대응

다른 팀이 당신의 master 브랜치에서 취약점을 발견하면:
1. Issue에 "unintended" 라벨이 붙음
2. `round_frequency`초마다 점수가 누적됨
3. **빨리 패치해야 합니다!**

```bash
cd my-service-repo
# 취약점 수정
vi service.py

# 패치 커밋 & push
git add .
git commit -m "Fix unintended vulnerability"
git push origin master
```

채점기가 다음 라운드에서 새 커밋에 대해 exploit을 재실행합니다.
- exploit 실패 → 방어 성공! 점수 누적 중단
- exploit 성공 → 점수 계속 누적

### 주의사항
- master 브랜치만 방어 대상입니다
- bug 브랜치는 수정하지 마세요 (intended 취약점은 고정 점수)
- 패치가 서비스 정상 동작을 깨뜨리지 않도록 주의

## 점수 확인

```bash
python3 gitctf.py score
# → score.html 생성 (브라우저에서 열기)
```

또는 웹 대시보드 (강사가 Docker Compose로 운영 시):
- http://localhost:8080

## 전략 팁

### 공격 전략
- 여러 팀의 서비스를 동시에 분석
- bug 브랜치와 master의 diff를 비교하면 의도된 취약점 힌트를 얻을 수 있음
- Unintended 취약점은 시간 누적이므로 빨리 발견할수록 유리

### 방어 전략
- 서비스 코드를 최소화하여 공격 표면 줄이기
- 입력 검증을 철저히
- Unintended 취약점이 발견되면 즉시 패치
