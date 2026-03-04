"""GitCTF 시스템 서비스 스켈레톤

socat을 통해 TCP 연결 시 이 스크립트가 실행됩니다.
stdin/stdout으로 클라이언트와 통신합니다.
"""

import sys
import os


FLAG_PATH = "/var/ctf/flag"


def read_flag():
    try:
        with open(FLAG_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "NO_FLAG"


def main():
    flag = read_flag()

    print("=== CTF Service v1.0 ===")
    print("1. View message")
    print("2. Admin panel")
    print("3. Exit")
    sys.stdout.flush()

    while True:
        try:
            choice = input("> ").strip()
        except EOFError:
            break

        if choice == "1":
            print("Hello, welcome to the service!")
        elif choice == "2":
            # TODO: 인증을 추가하세요.
            # 현재는 누구나 플래그를 읽을 수 있습니다!
            password = input("Password: ").strip()
            if password == "admin":
                print(f"Flag: {flag}")
            else:
                print("Wrong password!")
        elif choice == "3":
            print("Bye!")
            break
        else:
            print("Invalid choice")

        sys.stdout.flush()


if __name__ == "__main__":
    main()
