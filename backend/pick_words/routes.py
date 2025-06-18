# backend/pick_words/routes.py
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from firebase_admin import firestore
from auth.utils import auth_required

bp = Blueprint('pick_words', __name__, url_prefix='/pick_words')
db = firestore.client()
@bp.route('', methods=['GET'])
@auth_required
def pick_words():
    """
    取出 n 個最該複習的單字，依照 dueDate 升冪排序
    query param: ?limit=10
    """
    user_id = g.user['sub']
    limit = int(request.args.get('limit', 10))
    now = datetime.utcnow()
    docs = (
        db.collection("words")
          .where("userId", "==", user_id)
          .where("dueDate", "<=", now)
          .order_by("dueDate")
          .limit(limit)
          .stream()
    )

    words = []
    for doc in docs:
        data = doc.to_dict()
        words.append({
            "id": doc.id,
            "word": doc.id,
            "interval": data.get("lastInterval"),
            "easiness": data.get("easeFactor"),
            "next_review": data.get("dueDate").isoformat() if data.get("dueDate") else None,
            "short": data.get("short", ""),
            "full": data.get("full", "")
        })


    return jsonify(words), 200
