
import logging
import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase_client import supabase

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')



# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: 通常ログイン処理
        return redirect(url_for('login'))
    return render_template('login.html')

# Google認証開始
@app.route('/login/google')
def login_google():
    from config import DATABASE_URL
    redirect_url = url_for('google_callback', _external=True)
    # Supabase AuthのGoogle認証エンドポイント
    auth_url = f"{DATABASE_URL}/auth/v1/authorize?provider=google&redirect_to={redirect_url}"
    return redirect(auth_url)

# Google認証コールバック
@app.route('/auth/callback')
def google_callback():
    # Supabase Authのセッション情報（アクセストークン）を取得
    access_token = request.args.get('access_token')
    if not access_token:
        flash('Google認証後のアクセストークンが取得できませんでした。')
        return redirect(url_for('login'))

    # Supabase REST APIでUsersテーブルからユーザー情報取得
    from config import DATABASE_URL, DATABASE_API_KEY
    headers = {
        "apikey": DATABASE_API_KEY,
        "Authorization": f"Bearer {access_token}"
    }
    users_url = f"{DATABASE_URL}/rest/v1/auth.users"
    response = requests.get(users_url, headers=headers)
    logging.info('Supabase API status: %s', response.status_code)
    logging.info('Supabase API response: %s', response.text)
    if response.status_code != 200:
        flash('ユーザー情報の取得に失敗しました。')
        return redirect(url_for('login'))
    users = response.json()
    logging.info('Supabase API parsed users: %s', users)
    if not users:
        flash('ユーザー情報が見つかりませんでした。')
        return redirect(url_for('login'))
    user_info = users[0]
    user_email = user_info.get('email')
    google_id = user_info.get('id')
    name = user_info.get('user_metadata', {}).get('full_name')
    # accountsテーブルで照合
    result = supabase.table('accounts').select('*').eq('email', user_email).execute()
    if result.data:
        # 既存ユーザー
        session['user'] = user_email
        flash('ログインしました')
    else:
        # 新規登録
        supabase.table('accounts').insert({
            'email': user_email,
            'google_id': google_id,
            'name': name
        }).execute()
        session['user'] = user_email
        flash('新規登録しました')
    return redirect(url_for('home'))


# トップページ（ルート）
@app.route('/')
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('home.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
