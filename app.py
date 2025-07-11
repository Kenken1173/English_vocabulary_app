# app.py

import os
from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/add', methods=['POST'])
def add_word():
    """
    フォームから送信された新しい単語をSupabaseに登録します。
    """
    try:
        # フォームからデータを取得
        word = request.form.get('word')
        meaning = request.form.get('meaning')
        importance = request.form.get('importance')

        # 簡単なバリデーション
        if not word or not meaning or not importance:
            # 必須項目が空の場合は何もしないでトップページに戻る
            return redirect(url_for('index'))

        # Supabaseに挿入するデータを作成
        data_to_insert = {
            'word': word,
            'meaning': meaning,
            'importance': int(importance)
        }
        
        # 'word'テーブルにデータを挿入
        supabase.table('word').insert(data_to_insert).execute()

    except Exception as e:
        # エラーが発生した場合はコンソールに出力
        print(f"Error adding data to Supabase: {e}")
    
    # 登録後はトップページにリダイレクトして結果を反映
    return redirect(url_for('index'))


if __name__ == '__main__':
    # デバッグモードでアプリケーションを実行
    app.run(debug=True)