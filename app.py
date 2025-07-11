# app.py

import os
from flask import Flask, render_template
from supabase import create_client, Client
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# Supabaseの接続情報を環境変数から取得
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Supabaseクライアントの初期化
supabase: Client = create_client(url, key)

@app.route('/')
def index():
    """
    トップページを表示します。
    Supabaseから単語リストを取得し、テンプレートに渡します。
    """
    try:
        # 'word'テーブルから全てのデータを取得（idの昇順でソート）
        response = supabase.table('word').select("*").order('id', desc=False).execute()
        
        # 取得したデータをwords変数に格納
        words = response.data
        
    except Exception as e:
        # エラーが発生した場合は空のリストを渡し、コンソールにエラーを出力
        words = []
        print(f"Error fetching data from Supabase: {e}")

    # index.htmlをレンダリングし、取得した単語リストを渡す
    return render_template('index.html', words=words)

if __name__ == '__main__':
    # デバッグモードでアプリケーションを実行
    app.run(debug=True)