from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
from supabase_client import supabase

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
    # Supabaseからアクセストークンなどがクエリパラメータで返される
    user_email = request.args.get('user_email')
    google_id = request.args.get('provider_id')
    name = request.args.get('user_name')
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
