import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from firebase_admin import firestore
import openai
from lexile import approximate_lexile as lexile_score

# 建立Blueprint並設定路徑前綴
bp = Blueprint('articles', __name__, url_prefix='/articles')
db = firestore.client()

# 設定 OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@bp.route('', methods=['POST'])
def create_article():
    """
    建立新文章：
    1. 呼叫GPT-4o產文並計算 Lexile 分數
    2. 將文章存入Firestore（同時儲存目標與實際分數）
    3. 回傳文章ID / 內容 / 評估分數
    """
    data = request.get_json(force=True)
    # 使用者希望的文章難度（Lexile 分數）
    lexileTarget = data.get("lexileTarget", 800)
    # 希望出現在文章中的單字列表
    targetWords = data.get("targetWords", [])

    # 呼叫 GPT-4o 生成文章
    prompt = (
        f"Please write a short English passage with a Lexile score around {lexileTarget}. "
        f"Include at least these words: {', '.join(targetWords)}."
    )
    resp = openai.chat.completions.create(
        model="gpt-4o-mini", #測試先用便宜方案
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    article_text = resp.choices[0].message.content.strip()

    # 計算實際Lexile分數
    lexileActual = lexile_score(article_text)

    # 存入Firestore
    doc_ref = db.collection("articles").document()
    doc_ref.set({
        "lexileTarget": lexileTarget,
        "lexileActual": lexileActual,
        "targetWords": targetWords,
        "article": article_text,
        "createdAt": datetime.utcnow()
    })

    # 回傳結果
    return jsonify(
        id=doc_ref.id,
        article=article_text,
        lexileTarget=lexileTarget,
        lexileActual=lexileActual
    ), 201

@bp.route('', methods=['GET'])
def list_articles():
    """
    列出所有文章，包含目標與實際難度
    """
    docs = db.collection("articles").order_by("createdAt").stream()
    articles = [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]
    return jsonify(articles=articles), 200

@bp.route('/<article_id>', methods=['GET'])
def get_article(article_id):
    """
    取得單篇文章詳情，含 lexileTarget 與 lexileActual
    """
    doc = db.collection("articles").document(article_id).get()
    if not doc.exists:
        return jsonify(error="Article not found"), 404
    data = doc.to_dict()
    data["id"] = doc.id
    return jsonify(data), 200

@bp.route('/<article_id>', methods=['PUT'])
def update_article(article_id):
    """
    更新文章的 lexileTarget 或 targetWords
    """
    data = request.get_json(force=True)
    update_fields = {}
    if "lexileTarget" in data:
        update_fields["lexileTarget"] = data["lexileTarget"]
    if "targetWords" in data:
        update_fields["targetWords"] = data["targetWords"]
    if not update_fields:
        return jsonify(error="No fields to update"), 400

    db.collection("articles").document(article_id).update(update_fields)
    return jsonify(message="article updated"), 200

@bp.route('/<article_id>', methods=['DELETE'])
def delete_article(article_id):
    """
    刪除指定文章
    """
    db.collection("articles").document(article_id).delete()
    return '', 204
