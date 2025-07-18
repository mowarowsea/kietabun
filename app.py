from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
load_dotenv()
import os
import requests

app = Flask(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_ANON_KEY = os.environ['SUPABASE_ANON_KEY']
SUPABASE_API_KEY = os.environ['SUPABASE_API_KEY']

@app.route("/")
def index():
    return render_template("index.html", supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)


@app.route("/api/secure-data")
def secure_data():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    token = auth_header.split(" ")[1]

    # Supabaseにトークン検証依頼（またはjwtデコードする）
    userinfo = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={"Authorization": f"Bearer {token}"}
    )

    if userinfo.status_code != 200:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"message": "こんにちは！", "user": userinfo.json()})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)