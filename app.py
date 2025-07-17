

import logging
import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase_client import supabase

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')



# ログインページ
from config import SUPABASE_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: 通常ログイン処理
        return redirect(url_for('login'))
    return render_template('login.html', config={
        'SUPABASE_URL': SUPABASE_URL or '',
        'SUPABASE_ANON_KEY': SUPABASE_ANON_KEY or ''
    })

# /auth/callbackルート（jsでトークン処理）
@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    if not code:
        flash('認証コードが必要です。', 'error')
        return redirect(url_for('login'))
    
    url = f"{SUPABASE_URL}/auth/v1/callback?grant_type=pkce"
    data = {
        "auth_code": code,
        "code_verifier": session.get('code_verifier')
    }
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        flash('認証に失敗しました。', 'error')
        return redirect(url_for('login'))
    
    user_info = response.json().get('user', {})


    # accountsテーブルで照合
    result = supabase.table('accounts').select('*').eq('email', user_info.get("email")).execute()
    if result.data == False:
        # 新規登録
        supabase.table('accounts').insert({
            'email': user_info.get('email'),
            'google_id': user_info.get('id'),
            'name': user_info.get('user_metadata', {}).get('full_name')
        }).execute()

    session['access_token'] = response.json().get('access_token')
    session['user'] = response.json().get('user')
    return render_template('auth_callback.html', user=session['user'], access_token=session['access_token'])

# JSからPOSTされたaccess_tokenでサーバーセッションをセット
from flask import jsonify
@app.route('/api/session', methods=['POST'])
def api_session():
    data = request.get_json()
    access_token = data.get('access_token')
    if not access_token:
        return jsonify({'error': 'access_token required'}), 400
    from config import SUPABASE_URL, SUPABASE_API_KEY
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {access_token}"
    }
    users_url = f"{SUPABASE_URL}/rest/v1/auth.users"
    response = requests.get(users_url, headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'ユーザー情報の取得に失敗しました。'}), 401
    users = response.json()
    if not users:
        return jsonify({'error': 'ユーザー情報が見つかりませんでした。'}), 401
    user_info = users[0]
    user_email = user_info.get('email')
    google_id = user_info.get('id')
    name = user_info.get('user_metadata', {}).get('full_name')
    # accountsテーブルで照合
    result = supabase.table('accounts').select('*').eq('email', user_email).execute()
    if result.data:
        # 既存ユーザー
        session['user'] = user_email
    else:
        # 新規登録
        supabase.table('accounts').insert({
            'email': user_email,
            'google_id': google_id,
            'name': name
        }).execute()
        session['user'] = user_email
    return jsonify({'ok': True})


# トップページ（ルート）
@app.route('/')
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('home.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
