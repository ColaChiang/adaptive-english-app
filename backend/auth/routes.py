import os
import jwt, bcrypt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from firebase_admin import firestore
from auth.utils import auth_required

bp = Blueprint("auth", __name__, url_prefix="/auth")
db = firestore.client()
SECRET_KEY = os.getenv("JWT_SECRET", "replace-with-your-secret")

@bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    email = data.get("email")
    pwd   = data.get("password")
    if not email or not pwd:
        return jsonify(error="email and password required"), 400

    pw_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
    db.collection("users").document(email).set({
        "email": email,
        "passwordHash": pw_hash,
        "createdAt": datetime.utcnow()
    })
    return jsonify(message="signup success"), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data.get("email")
    pwd   = data.get("password")
    if not email or not pwd:
        return jsonify(error="email and password required"), 400

    doc = db.collection("users").document(email).get()
    if not doc.exists:
        return jsonify(error="invalid credentials"), 401
    user = doc.to_dict()
    if not bcrypt.checkpw(pwd.encode(), user["passwordHash"].encode()):
        return jsonify(error="invalid credentials"), 401

    token = jwt.encode({
        "sub": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")
    return jsonify(token=token), 200

@bp.route("/me", methods=["GET"])
@auth_required
def me():
    return jsonify(email=g.user["sub"]), 200