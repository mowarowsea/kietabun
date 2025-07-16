// SupabaseのURLとanonキーを環境変数から取得してクライアントJSで使う
export const SUPABASE_URL = window.env?.SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = window.env?.SUPABASE_ANON_KEY || '';
