# conftest.py
import pytest
from main import app  # 假設你的 Flask 叫 app
from models.models import Product  # 依你的結構引入你的 model
from dbconfig.dbconnect import db  # 依你的結構引入你的 db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# test_click.py
def test_click_success(client):

    response = client.post("/click/P01")
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "點擊次數已更新"
    assert data["clickTimes"] == 6  # 原本5，加1變6

def test_click_not_found(client):
    response = client.post("/click/not_exist_id")
    data = response.get_json()

    assert response.status_code == 404
    assert data["error"] == "未找到資源"