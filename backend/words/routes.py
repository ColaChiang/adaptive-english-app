# backend/words/routes.py
from flask import Blueprint, request, jsonify, g
from auth.utils import auth_required
from datetime import datetime
from firebase_admin import firestore
import random
# import requests
import openai
bp = Blueprint('words', __name__, url_prefix='/words')
db = firestore.client()

@bp.route('', methods=['POST'])
@auth_required
def create_or_mark_word():
    """
    建立新單字或標記文章中的單字，並自動翻譯與儲存。
    """
    data = request.get_json(force=True)
    user_id = g.user["sub"]
    word = data.get('word')
    level = data.get('level', 'A1')
    if not word:
        return jsonify(error="word is required"), 400

    doc_ref = db.collection("words").document(word)
    doc = doc_ref.get()

    if doc.exists and doc.to_dict().get("userId") == user_id:
        # 更新熟悉度（再次點擊 = 還不熟，quality=2）
        from sm2 import sm2_review  # 確保已 import
        word_data = doc.to_dict()
        update = sm2_review(
            last_interval=word_data.get("lastInterval", 0),
            ease_factor=word_data.get("easeFactor", 2.5),
            quality=2
        )
        doc_ref.update({
            "lastInterval": update["interval"],
            "easeFactor": update["easeFactor"],
            "dueDate": update["dueDate"]
        })
        return jsonify(
            word=word,
            short=word_data.get("short", "無翻譯"),
            full=word_data.get("full", "無解釋"),
            existed=True
        ), 200

    # 呼叫 OpenAI 翻譯與解釋
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a concise English-to-Tranditional Chinese dictionary assistant. Provide clear and short definitions."
            },
            {
                "role": "user",
                "content": f"Translate the English word '{word}' into the shortest possible Tranditional Chinese meaning. Just output a few Tranditional Chinese words, no punctuation or explanation."
            },
            {
                "role": "user",
                "content": f"Then give a brief Tranditional Chinese explanation of '{word}', including the part of speech (e.g., n., v., adj.). Use simple language in one or two lines. Keep it short and clear. Separate the two parts with 3 hyphens (---)."
            }
        ]
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=150
        )
        parts = response.choices[0].message.content.strip().split('---', 1)
        short = parts[0].strip()
        full = parts[1].strip() if len(parts) > 1 else short
    except Exception as e:
        short = "翻譯失敗"
        full = str(e)

    # 新增新單字資料
    doc_ref.set({
        "userId": user_id,
        "createdAt": datetime.utcnow(),
        "lastInterval": 0,
        "easeFactor": 2.5,
        "dueDate": datetime.utcnow(),
        "short": short,
        "full": full,
        "reviewCount": 0
    })

    return jsonify(
        word=word,
        short=short,
        full=full,
        existed=False
    ), 201


@bp.route('', methods=['GET'])
@auth_required
def list_words():
    user_id = g.user["sub"]
    docs = db.collection("words").where("userId","==",user_id).order_by("createdAt").stream()
    words = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify(words=words), 200

@bp.route('/<word_id>', methods=['PUT'])
@auth_required
def update_word(word_id):
    user_id = g.user["sub"]
    data = request.get_json(force=True)

    # 1. 先取出該文件，確保它屬於當前使用者
    doc_ref = db.collection("words").document(word_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("userId") != user_id:
        return jsonify(error="Not found or unauthorized"), 404

    # 2. 只更新 level（或你允許的欄位）
    update_fields = {}
    if "level" in data:
        update_fields["level"] = data["level"]
    if not update_fields:
        return jsonify(error="No fields to update"), 400

    doc_ref.update(update_fields)
    return jsonify(message="word updated"), 200

@bp.route('/<word_id>', methods=['DELETE'])
@auth_required
def delete_word(word_id):
    user_id = g.user["sub"]

    # 1. 確認擁有權
    doc_ref = db.collection("words").document(word_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("userId") != user_id:
        return jsonify(error="Not found or unauthorized"), 404

    # 2. 刪除
    doc_ref.delete()
    return '', 204

@bp.route('/quiz', methods=['GET'])
@auth_required
def generate_quiz():
    user_id = g.user["sub"]
    docs = db.collection("words").where("userId", "==", user_id).stream()
    word_list = [doc.id for doc in docs]

    if len(word_list) < 4:
        return jsonify(error="需要至少 4 個單字才能生成測驗"), 400

    selected_words = random.sample(word_list, min(10, len(word_list)))
    questions = []

    for target_word in selected_words:
        others = [w for w in word_list if w != target_word]
        distractors = random.sample(others, min(3, len(others)))
        options = distractors + [target_word]
        random.shuffle(options)

        prompt = f"Create a TOEIC-style fill-in-the-blank sentence using the word '{target_word}', with a blank for the word."
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an English teacher generating quiz questions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80
        )
        sentence = response.choices[0].message.content.strip()

        questions.append({
            "question": sentence,
            "options": options,
            "answer": target_word
        })

    return jsonify(questions=questions), 200

# @bp.route('/mark', methods=['POST'])
# @auth_required
# def mark_word():
#     data = request.get_json(force=True)
#     user_id = g.user["sub"]
#     word = data.get("word")
#     if not word:
#         return jsonify(error="Missing word"), 400

#     doc_ref = db.collection("words").document(word)
#     doc = doc_ref.get()

#     if not doc.exists:
#         doc_ref.set({
#             "userId": user_id,
#             "level": "A1",
#             "createdAt": datetime.utcnow(),
#             "lastInterval": 0,
#             "easeFactor": 2.5,
#             "dueDate": datetime.utcnow()
#         })

#     # 使用 LibreTranslate API 取得翻譯
#     try:
#         resp = requests.post(
#             "https://libretranslate.com/translate",
#             json={
#                 "q": word,
#                 "source": "auto",
#                 "target": "zh-TW",
#                 "format": "text",
#                 "api_key": ""  # 你可以註冊自己的 key 或留空（會限流）
#             },
#             headers={"Content-Type": "application/json"},
#             timeout=5
#         )
#         resp.raise_for_status()
#         translation = resp.json().get("translatedText", "無翻譯")
#     except Exception as e:
#         translation = "翻譯失敗"

#     return jsonify(word=word, meaning=translation), 200