import os
import jwt
from flask import request, jsonify, g
from functools import wraps

SECRET_KEY = os.getenv("JWT_SECRET", "replace-with-your-secret")

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Missing token"), 401
        token = header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify(error="Token expired"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token"), 401
        g.user = payload  # payload['sub'] 就是 userId/email
        return f(*args, **kwargs)
    return wrapper