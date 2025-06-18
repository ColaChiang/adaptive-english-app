# backend/app.py
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

load_dotenv()
GOOGLE_CRED = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 初始化 Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(GOOGLE_CRED)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 初始化 OpenAI (文章 Blueprint 內也要設定 key)
client = OpenAI(api_key=OPENAI_KEY)

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello LLM World 👋")

# 註冊剛才拆出的三個 Blueprint
from words.routes import bp as words_bp
from articles.routes import bp as articles_bp
from auth.routes import bp as auth_bp
from review.routes import bp as review_bp
from pick_words.routes import bp as pick_words_bp

app.register_blueprint(auth_bp)
app.register_blueprint(words_bp)
app.register_blueprint(articles_bp)
app.register_blueprint(review_bp)
app.register_blueprint(pick_words_bp)

if __name__ == "__main__":
    app.run(debug=True)