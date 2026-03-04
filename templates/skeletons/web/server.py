"""GitCTF 웹 서비스 스켈레톤

이 파일을 수정하여 서비스를 개발하세요.
플래그는 /var/ctf/flag 파일에서 읽습니다.
"""

import os

from flask import Flask, request, jsonify

app = Flask(__name__)
FLAG_PATH = "/var/ctf/flag"


def read_flag():
    try:
        with open(FLAG_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "NO_FLAG"


@app.route("/")
def index():
    return "<h1>My CTF Service</h1><p>Service is running!</p>"


@app.route("/api/data")
def get_data():
    # TODO: 여기에 서비스 기능을 구현하세요.
    # 예: 데이터베이스 조회, 파일 읽기 등
    return jsonify({"message": "Hello from CTF service"})


@app.route("/api/flag")
def get_flag():
    # TODO: 이 엔드포인트에 인증을 추가하세요.
    # 현재는 누구나 플래그를 읽을 수 있습니다!
    return jsonify({"flag": read_flag()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=False)
