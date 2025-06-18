# backend/review/routes.py
from flask import Blueprint, request, jsonify, g
from datetime import datetime
from firebase_admin import firestore
from sm2 import next_interval, due_date_from_interval
from auth.utils import auth_required

bp = Blueprint("review", __name__, url_prefix="/review")
db = firestore.client()

@bp.route("/due", methods=["GET"])
@auth_required
def list_due_words():
    """取出今天該做複習的單字清單"""
    user_id = g.user["sub"]
    today = datetime.utcnow()
    docs = (db.collection("words")
              .where("userId", "==", user_id)
              .where("dueDate", "<=", today)
              .stream())
    words = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify(words=words), 200

@bp.route("/feedback", methods=["POST"])
@auth_required
def review_feedback():
    """
    回報一次複習：
    body: { "wordId": "...", "quality": 0~5 }
    回傳更新後的間隔與下次複習日期
    """
    user_id = g.user["sub"]
    data = request.get_json(force=True)
    word_id = data.get("wordId")
    quality = data.get("quality")
    if word_id is None or quality is None:
        return jsonify(error="wordId and quality required"), 400

    doc_ref = db.collection("words").document(word_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("userId") != user_id:
        return jsonify(error="Not found or unauthorized"), 404

    w = doc.to_dict()
    old_interval = w.get("lastInterval", 0)
    ef = w.get("easeFactor", 2.5)

    new_interval, new_ef = next_interval(old_interval, quality, ef)
    next_due = due_date_from_interval(new_interval)

    doc_ref.update({
        "lastInterval": new_interval,
        "easeFactor":   new_ef,
        "dueDate":      next_due,
        "reviewCount": firestore.Increment(1)

    })

    return jsonify(
      wordId=word_id,
      interval=new_interval,
      easeFactor=new_ef,
      nextDue=next_due.isoformat()
    ), 200