import os
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()  # 讀取 .env

# 初始化 Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello LLM World 👋")

# ➜ 新增 API：寫入單字
@app.route("/add_word", methods=["POST"])
def add_word():
    data = request.get_json()
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

if __name__ == "__main__":
    app.run(debug=True)
