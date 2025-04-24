import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from firebase_admin import firestore
import openai
from lexile import approximate_lexile as lexile_score

bp = Blueprint('articles', __name__, url_prefix='/articles')
db = firestore.client()
openai.api_key = os.getenv("OPENAI_API_KEY")

@bp.route('', methods=['POST'])
def create_article():
    data = request.get_json(force=True)
    level = data.get("level", 800)
    target_words = data.get("target_words", [])

    prompt = (
        f"Please write a short English passage with a Lexile score around {level}. "
        f"Include at least these words: {', '.join(target_words)}."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}],
        max_tokens=300,
    )
    article = response.choices[0].message.content.strip()
    lex = lexile_score(article)

    # 如果要存檔，可在此呼叫 Firestore
    # doc = db.collection("articles").document()
    # doc.set({...})

    return jsonify(article=article, lexile=lex), 200

@bp.route('', methods=['GET'])
def list_articles():
    docs = db.collection("articles").order_by("createdAt").stream()
    articles = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify(articles=articles), 200