import pytest
import sys
import os
# 將主目錄加入 Python 模組搜尋路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_track_list(client):
    res = client.post("/clientPage/trackList", json={"cId": "C01"})
    assert res.status_code in [200, 404]
    if res.status_code == 200:
        assert "results" in res.get_json()

def test_get_client_data(client):
    res = client.post("/clientPage/client", json={"cId": "C01"})
    assert res.status_code in [200, 404]
    if res.status_code == 200:
        assert "results" in res.get_json()

def test_update_client_data(client):
    res = client.post("/clientPage/data/update", json={
        "cId": "C01",
        "cName": "單元測試使用者",
        "email": "pytest@example.com",
        "phone": "0912345678",
        "sex": "男"
    })
    assert res.status_code in [200, 400]
    assert "message" in res.get_json()

def test_password_update(client):
    res = client.post("/clientPage/password/update", json={
        "cId": "C01",
        "password": "Test@123456"
    })
    assert res.status_code in [200, 400, 500]
    data = res.get_json()
    assert "message" in data or "error" in data
