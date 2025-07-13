from supabase import create_client, Client
from config import DATABASE_URL, DATABASE_API_KEY

supabase: Client = create_client(DATABASE_URL, DATABASE_API_KEY)

# サンプル: ユーザー一覧取得
# response = supabase.table('users').select('*').execute()
# print(response)
