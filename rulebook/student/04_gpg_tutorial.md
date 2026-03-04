# 참가자 가이드 — 4. GPG 키 설정

## GPG란?

PGP (Pretty Good Privacy) 암호화를 사용하여 익스플로잇을 안전하게 전송합니다.
공격자가 제출한 익스플로잇은 GPG로 암호화되어 대상 팀만 복호화할 수 있습니다.

## GPG 키 생성

```bash
gpg --full-generate-key
```

프롬프트 안내:
1. 키 종류: `RSA and RSA` (기본값)
2. 키 크기: `4096`
3. 만료 기간: `0` (만료 없음)
4. 이름, 이메일 입력
5. 비밀번호 설정

## 키 확인

```bash
# 공개키 목록
gpg --list-keys

# 개인키 목록
gpg --list-secret-keys
```

## 공개키 내보내기

```bash
# 텍스트 형식으로 내보내기
gpg --armor --export YOUR_KEY_ID > my_public_key.asc
```

출력 파일 확인:
```
-----BEGIN PGP PUBLIC KEY BLOCK-----
... (이것이 공개키입니다!)
-----END PGP PUBLIC KEY BLOCK-----
```

## ⚠️ 절대 하지 말아야 할 것

> **개인키(PRIVATE KEY)를 절대 제출하지 마세요!**

개인키 파일에는 다음 문구가 포함됩니다:
```
-----BEGIN PGP PRIVATE KEY BLOCK-----
```

이것이 보이면 **잘못된 파일**입니다. 공개키만 제출하세요!

## 키 검증

GitCTF CLI로 키 파일을 검증할 수 있습니다:
```bash
gitctf check-key my_public_key.asc
```

또는 웹 GUI에서 팀 관리 → 공개키 업로드를 사용하세요.

## 다른 팀 공개키 가져오기

관리자가 다른 팀의 공개키를 배포하면:
```bash
gpg --import team_alpha_public.asc
```
