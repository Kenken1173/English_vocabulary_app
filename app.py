# app.py

import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# 修正点: セッションの秘密鍵を.envファイルから読み込む固定値に変更
# これにより、サーバーがリロードしてもセッションが維持されるようになります。
# 以前の os.urandom(24) は毎回違う値を生成するため、ログインが維持できない原因でした。
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
app.secret_key = os.environ.get('SECRET_KEY')

# Supabaseの接続情報を環境変数から取得
url: str = os.environ.get("SUPABASE_URL")
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# Supabaseクライアントの初期化
supabase: Client = create_client(url, service_key)


@app.route('/')
def landing():
    """
    クイズか管理画面かを選択するトップページを表示します。
    """
    return render_template('landing.html')


# ★★★ ここから認証関連のルートを追加・修正 ★★★

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    ログインページ。パスワード認証を行います。
    """
    # フォームからPOSTリクエストが来た場合
    if request.method == 'POST':
        password = request.form.get('password')
        # .envファイルに設定したパスワードと一致するかチェック
        if password == os.environ.get('ADMIN_PASSWORD'):
            session['logged_in'] = True # セッションに「ログイン済み」の印を付ける
            flash('ログインしました。', 'success')
            return redirect(url_for('manage'))
        else:
            flash('パスワードが違います。', 'error')
            
    # GETリクエストの場合、またはパスワードが違った場合はログインページを表示
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    ログアウト処理。セッション情報を削除します。
    """
    session.pop('logged_in', None) # セッションからログイン情報を削除
    flash('ログアウトしました。', 'info')
    return redirect(url_for('landing'))


@app.route('/manage')
def manage():
    """
    単語の登録・一覧画面。アクセス時にログイン状態をチェックします。
    """
    # セッションに「ログイン済み」の印がなければ、ログインページに飛ばす
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # --- 以下は既存の処理 ---
    try:
        response = supabase.table('words').select("*").order('id', desc=False).execute()
        words = response.data
    except Exception as e:
        words = []
        print(f"Error fetching data from Supabase: {e}")
    return render_template('manage.html', words=words)


@app.route('/add', methods=['POST'])
def add_word():
    """
    新しい単語をSupabaseに登録します。
    """
    # この操作もログインが必要
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        word = request.form.get('word')
        meaning = request.form.get('meaning')
        importance = request.form.get('importance')

        if not word or not meaning or not importance:
            return redirect(url_for('manage')) 

        data_to_insert = {
            'word': word,
            'meaning': meaning,
            'importance': int(importance)
        }
        supabase.table('words').insert(data_to_insert).execute()
        flash('新しい単語を登録しました。', 'success')
    except Exception as e:
        print(f"Error adding data to Supabase: {e}")
        flash('登録中にエラーが発生しました。', 'error')
    
    return redirect(url_for('manage'))


@app.route('/quiz')
def quiz():
    """
    クイズページを表示します。
    """
    try:
        response = supabase.table('words').select("word, meaning").execute()
        all_words = response.data
        
        if all_words:
            quiz_word = random.choice(all_words)
        else:
            quiz_word = None
            
    except Exception as e:
        print(f"Error fetching quiz data: {e}")
        quiz_word = None

    return render_template('quiz.html', word=quiz_word)


if __name__ == '__main__':
    app.run(debug=True)
