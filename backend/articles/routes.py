# backend/articles/routes.py
import os
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from firebase_admin import firestore
import openai
from lexile import approximate_lexile as lexile_score
from auth.utils import auth_required

# 建立 Blueprint 並設定路徑前綴
bp = Blueprint('articles', __name__, url_prefix='/articles')
db = firestore.client()
openai.api_key = os.getenv("OPENAI_API_KEY")

@bp.route('', methods=['POST'])
@auth_required
def create_article():
    """
    建立新文章：
      1. 呼叫 GPT-4o 產文並計算 Lexile 分數
      2. 存入 Firestore（儲存 userId、目標與實際分數、關鍵字、內容、時間）
      3. 回傳新增文檔的 ID、文章內容、目標與實際 Lexile
    """
    user_id     = g.user['sub']
    data        = request.get_json(force=True)
    lexileTarget = data.get("lexileTarget", 800)
    targetWords  = data.get("targetWords", [])

    prompt = (
        f"Please write a short English passage with a Lexile score around {lexileTarget}. "
        f"Include at least these words: {', '.join(targetWords)}."
    )
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=300,
    )
    article_text = resp.choices[0].message.content.strip()

    # 計算實際Lexile分數
    lexileActual = lexile_score(article_text)

    # 存入Firestore
    doc_ref = db.collection("articles").document()
    doc_ref.set({
        "userId":       user_id,
        "lexileTarget": lexileTarget,
        "lexileActual": lexileActual,
        "targetWords":  targetWords,
        "article":      article_text,
        "createdAt":    datetime.utcnow()
    })

    return jsonify(
        id=doc_ref.id,
        article=article_text,
        lexileTarget=lexileTarget,
        lexileActual=lexileActual
    ), 201

@bp.route('', methods=['GET'])
@auth_required
def list_articles():
    """
    列出所有使用者自己的文章，包含目標與實際難度
    """
    user_id = g.user['sub']
    docs = (db.collection("articles")
              .where("userId", "==", user_id)
              .order_by("createdAt")
              .stream())
    articles = [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]
    return jsonify(articles=articles), 200

@bp.route('/<article_id>', methods=['GET'])
@auth_required
def get_article(article_id):
    """
    取得單篇文章詳情，僅限該使用者自己的文章
    """
    user_id = g.user['sub']
    doc_ref = db.collection("articles").document(article_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("userId") != user_id:
        return jsonify(error="Article not found or unauthorized"), 404

    data = doc.to_dict()
    data["id"] = doc.id
    return jsonify(data), 200

@bp.route('/<article_id>', methods=['PUT'])
@auth_required
def update_article(article_id):
    """
    更新文章的 lexileTarget 或 targetWords（只限本人）
    """
    user_id = g.user['sub']
    doc_ref = db.collection("articles").document(article_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("userId") != user_id:
        return jsonify(error="Article not found or unauthorized"), 404

    data = request.get_json(force=True)
    update_fields = {}
    if "lexileTarget" in data:
        update_fields["lexileTarget"] = data["lexileTarget"]
    if "targetWords" in data:
        update_fields["targetWords"] = data["targetWords"]
    if not update_fields:
        return jsonify(error="No fields to update"), 400

    doc_ref.update(update_fields)
    return jsonify(message="article updated"), 200

@bp.route('/<article_id>', methods=['DELETE'])
@auth_required
def delete_article(article_id):
    """
    刪除指定文章（只限本人）
    """
    user_id = g.user['sub']
    doc_ref = db.collection("articles").document(article_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("userId") != user_id:
        return jsonify(error="Article not found or unauthorized"), 404

    doc_ref.delete()
    return '', 204