import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import openai
from lexile import approximate_lexile as lexile_score

load_dotenv()

# 初始化 Firebase
if not firebase_admin._apps:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError("Missing Firebase credentials path in .env")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 初始化 OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Missing OpenAI API key in .env")

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello LLM World 👋")

# ➜ 寫入單字 API
@app.route("/add_word", methods=["POST"])
def add_word():
    data = request.get_json(force=True)
    word = data.get("word")
    level = data.get("level", "A1")
    if not word:
        return jsonify(error="word is required"), 400

    doc_ref = db.collection("words").document(word)
    doc_ref.set({
        "level": level,
        "createdAt": datetime.utcnow()
    })
    return jsonify(message=f"{word} saved", level=level), 201

# ➜ 生成文章並評估可讀性 API
@app.route("/generate_article", methods=["POST"])
def generate_article():
    data = request.get_json(force=True)
    level = data.get("level", 800)
    target_words = data.get("target_words", [])

    # 組裝 prompt
    prompt = (
        f"Please write a short English passage with a Lexile score around {level}. "
        f"Include at least these words: {', '.join(target_words)}."
    )
    # 使用 GPT-4o 生成文章
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    article = response.choices[0].message.content.strip()

    # 計算可讀性映射分數
    lexile = lexile_score(article)

    return jsonify(article=article, lexile=lexile)

if __name__ == "__main__":
    app.run(debug=True)