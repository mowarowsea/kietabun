import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'
import { SUPABASE_URL, SUPABASE_ANON_KEY } from './supabase_config.js';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: { flowType: 'pkce' }
});

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('google-login-btn');
  if (btn) {
    btn.addEventListener('click', async () => {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin + '/auth/callback'
        }
      });
      if (error) alert('Google認証エラー: ' + error.message);
    });
  }

  // コールバック時のトークン処理
  if (window.location.pathname === '/auth/callback') {
    supabase.auth.getSessionFromUrl({ storeSession: true }).then(async ({ data, error }) => {
      if (error) {
        alert('認証コールバックエラー: ' + error.message);
        window.location.href = '/login';
        return;
      }
      // サーバーにセッション情報を送信してログイン状態をセット
      const res = await fetch('/api/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: data.session.access_token })
      });
      if (res.ok) {
        window.location.href = '/';
      } else {
        alert('サーバーログイン失敗');
        window.location.href = '/login';
      }
    });
  }
});
