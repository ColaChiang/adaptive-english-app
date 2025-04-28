from flask import Blueprint, request, jsonify, g
from auth.utils import auth_required
from datetime import datetime
from firebase_admin import firestore

bp = Blueprint('words', __name__, url_prefix='/words')
db = firestore.client()

@bp.route('', methods=['POST'])
@auth_required
def create_word():
    data = request.get_json(force=True)
    user_id = g.user["sub"]
    word = data.get('word')
    level = data.get('level', 'A1')
    if not word:
        return jsonify(error="word is required"), 400

    db.collection("words").document(word).set({
        "userId": user_id,
        "level": level,
        "createdAt": datetime.utcnow()
    })
    return jsonify(message=f"{word} saved", level=level), 201

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