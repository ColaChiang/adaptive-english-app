# backend/articles/routes.py
import os
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from firebase_admin import firestore
import openai
from lexile import approximate_lexile as lexile_score
from auth.utils import auth_required
from sm2 import due_date_from_interval

# 建立 Blueprint 並設定路徑前綴
bp = Blueprint('articles', __name__, url_prefix='/articles')
db = firestore.client()
openai.api_key = os.getenv("OPENAI_API_KEY")

@bp.route('', methods=['POST'])
@auth_required
def create_article():
    """
    建立新文章：
    - 使用 GPT 產文，包含指定單字
    - 計算 Lexile 難度
    - 儲存於 Firestore，附帶分析資訊
    """
    user_id = g.user['sub']
    data = request.get_json(force=True)

    lexileTarget = data.get("lexileTarget")
    targetWords = data.get("targetWords")

    # 驗證欄位
    if not isinstance(lexileTarget, int):
        return jsonify(error="Invalid lexileTarget"), 400

    # 若未給 targetWords，則從使用者字典中自動挑選
    if not targetWords:
        docs = db.collection("words")\
                .where("userId", "==", user_id)\
                .order_by("dueDate")\
                .limit(5).stream()
        targetWords = [doc.id for doc in docs]

    if not targetWords:
        return jsonify(error="無法自動選取單字，請手動輸入至少一個單字"), 400


    # 組 prompt
    prompt = (
        f"Write a short, engaging English story around Lexile level {lexileTarget}. "
        f"Make sure to include these words: {', '.join(targetWords)}. "
        f"Keep it readable for learners, about 150-300 words long."
    )

    try:
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        article_text = resp.choices[0].message.content.strip()
    except Exception as e:
        return jsonify(error="GPT generation failed", detail=str(e)), 500

    # 計算 Lexile
    lexileActual = lexile_score(article_text)

    # 統計 targetWords 出現次數
    counts = {w.lower(): article_text.lower().count(w.lower()) for w in targetWords}

    doc_ref = db.collection("articles").document()
    doc_ref.set({
        "userId": user_id,
        "createdAt": datetime.utcnow(),
        "lexileTarget": lexileTarget,
        "lexileActual": lexileActual,
        "targetWords": targetWords,
        "wordCounts": counts,
        "article": article_text
    })

    return jsonify({
        "id": doc_ref.id,
        "article": article_text,
        "lexileTarget": lexileTarget,
        "lexileActual": lexileActual,
        "wordCounts": counts
    }), 201
    
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
@bp.route('', methods=['GET'])
@auth_required
def list_articles():
    """
    列出所有使用者自己的文章，包含目標與實際難度
    """
    user_id = g.user['sub']
    docs = (db.collection("articles")
              .where("userId", "==", user_id)
              .order_by("createdAt", direction=firestore.Query.DESCENDING)
              .stream())
    articles = [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]
    return jsonify(articles=articles), 200

@bp.route('/<article_id>/mark_unknown', methods=['POST'])
@auth_required
def mark_unknown_word(article_id):
    user_id = g.user['sub']
    data = request.get_json(force=True)
    word = data.get("word", "").strip().lower()

    if not word:
        return jsonify(error="Missing word"), 400

    doc_ref = db.collection("words").document(f"{user_id}_{word}")
    doc_ref.set({
        "userId": user_id,
        "word": word,
        "lastInterval": 0,
        "easeFactor": 2.5,
        "dueDate": due_date_from_interval(0),
        "createdAt": datetime.utcnow()
    })

    return jsonify(message="Word marked as unknown and saved"), 200