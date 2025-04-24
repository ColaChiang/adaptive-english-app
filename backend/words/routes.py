from flask import Blueprint, request, jsonify
from datetime import datetime
from firebase_admin import firestore

bp = Blueprint('words', __name__, url_prefix='/words')
db = firestore.client()

@bp.route('', methods=['POST'])
def create_word():
    data = request.get_json(force=True)
    word = data.get('word')
    level = data.get('level', 'A1')
    if not word:
        return jsonify(error="word is required"), 400

    db.collection("words").document(word).set({
        "level": level,
        "createdAt": datetime.utcnow()
    })
    return jsonify(message=f"{word} saved", level=level), 201

@bp.route('', methods=['GET'])
def list_words():
    docs = db.collection("words").order_by("createdAt").stream()
    words = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify(words=words), 200

@bp.route('/<word_id>', methods=['PUT'])
def update_word(word_id):
    data = request.get_json(force=True)
    db.collection("words").document(word_id).update(data)
    return jsonify(message="word updated"), 200

@bp.route('/<word_id>', methods=['DELETE'])
def delete_word(word_id):
    db.collection("words").document(word_id).delete()
    return '', 204