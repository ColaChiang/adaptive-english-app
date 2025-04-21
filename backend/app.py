import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI
from lexile import lexile_score

# 1. 讀取 .env，並設定金鑰
load_dotenv()
GOOGLE_CRED = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 2. 初始化 OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# 3. 建立 Flask app
app = Flask(__name__)

# 4. 初始化 Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(GOOGLE_CRED)
    firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/")
def index():
    return jsonify(message="Hello LLM World 👋")

@app.route("/add_word", methods=["POST"])
def add_word():
    data = request.get_json()
    word = data.get("word")
    level = data.get("level", "A1")
    if not word:
        return jsonify(error="word is required"), 400

    db.collection("words").document(word).set({
        "level": level,
        "createdAt": datetime.utcnow()
    })
    return jsonify(message=f"{word} saved", level=level), 201

# ─── 路由：產生文章並回傳 Lexile 分數 ────────────────
@app.route("/generate_article", methods=["POST"])
def generate_article():
    data = request.get_json()
    level = data.get("level", 800)
    target_words = data.get("target_words", [])

    # 1. 組 prompt
    prompt = (
        f"Please write a short English passage with a Lexile score around {level}. "
        f"Include at least these words: {', '.join(target_words)}.\n\nPassage:"
    )

    # 2. 呼叫 GPT-4 產文
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    article = resp.choices[0].message.content.strip()

    # 3. 計算實際 Lexile 分數
    lex = lexile_score(article)

    # 4. 回傳 JSON
    return jsonify(article=article, lexile=lex)

# 5. 啟動服務
if __name__ == "__main__":
    app.run(debug=True)