# backend/tests/test_pick_words.py
import os
import jwt
import pytest
from freezegun import freeze_time
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def make_token(sub="foo@example.com"):
    # 用你 .env 裡的 SECRET_KEY
    secret = os.getenv("JWT_SECRET", "replace-with-your-secret")
    return jwt.encode({"sub": sub, "exp": 9999999999}, secret, algorithm="HS256")

@freeze_time("2025-01-01T00:00:00Z")
def test_pick_words_empty(client):
    token = make_token()
    resp = client.get(
        "/pick_words?limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    # 檢查回傳結構有 words 欄位
    assert "words" in data
    assert isinstance(data["words"], list)