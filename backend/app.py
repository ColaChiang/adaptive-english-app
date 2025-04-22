import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI
from lexile import lexile_score

# 1. 讀取環境變數
load_dotenv()
GOOGLE_CRED = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 2. 初始化 Firebase
if not firebase_admin._apps:
    if not GOOGLE_CRED:
        raise RuntimeError("Missing Firebase credentials path in .env")
    cred = credentials.Certificate(GOOGLE_CRED)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 3. 初始化 OpenAI 客戶端
if not OPENAI_KEY:
    raise RuntimeError("Missing OpenAI API key in .env")
client = OpenAI(api_key=OPENAI_KEY)

# 4. 建立 Flask 應用
app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello LLM World 👋")

@app.route("/add_word", methods=["POST"])
def add_word():
    data = request.get_json(force=True)
    word = data.get("word")
    level = data.get("level", "A1")
    if not word:
        return jsonify(error="word is required"), 400

    db.collection("words").document(word).set({
        "level": level,
        "createdAt": datetime.utcnow()
    })
    return jsonify(message=f"{word} saved", level=level), 201

@app.route("/generate_article", methods=["POST"])
def generate_article():
    data = request.get_json(force=True)
    level = data.get("level", 800)
    target_words = data.get("target_words", [])

    # 組裝 Prompt
    prompt = (
        f"Please write a short English passage with a Lexile score around {level}. "
        f"Include at least these words: {', '.join(target_words)}.\n\nPassage:"
    )
    # 呼叫 GPT-4o 生成文章
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    article = resp.choices[0].message.content.strip()

    # 計算並回傳 Lexile 分數
    lex = lexile_score(article)
    return jsonify(article=article, lexile=lex), 200

if __name__ == "__main__":
    # 僅監聽本機
    app.run(debug=True)