import pytest
import json
import sys
import os
# 將主目錄加入 Python 模組搜尋路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# 測試 /clientPage/track 切換追蹤狀態 POST
def test_toggle_track(client):
    data = {"cId": "C01", "pId": "P01"}
    response = client.post("/clientPage/track", json=data)
    assert response.status_code == 200
    res = response.get_json()
    
    # 預期 message 為「已加入追蹤」或「已取消追蹤」
    assert res["message"] in ["已加入追蹤", "已取消追蹤"]
    assert res["cId"] == data["cId"]
    assert res["pId"] == data["pId"]
    assert res["status"] in [0, 1]

# 測試 /clientPage/trackList 查詢追蹤清單 POST
def test_get_track_list(client):
    data = {"cId": "C01"}
    response = client.post("/clientPage/trackList", json=data)
    assert response.status_code == 200
    res = response.get_json()
    assert "results" in res
    assert isinstance(res["results"], list)
    for item in res["results"]:
        assert "cId" in item and "pId" in item
        assert item["cId"] == data["cId"]

# 測試 /clientPage/client 查詢會員資料 POST
def test_get_client_data(client):
    data = {"cId": "C01"}
    response = client.post("/clientPage/client", json=data)
    assert response.status_code == 200
    res = response.get_json()
    assert "results" in res
    client_data = res["results"]
    assert client_data["cId"] == data["cId"]
    assert "cName" in client_data
    assert "account" in client_data
    assert "email" in client_data
    assert "phone" in client_data
    assert "sex" in client_data
    assert "birthday" in client_data

# 測試 /clientPage/data/update 成功與錯誤情況 POST
def test_update_client_data_success(client):
    data = {
        "cId": "C01",
        "cName": "test",
        "email": "test@mail.com",
        "phone": "0900000000",
        "sex": "女"
    }
    response = client.post("/clientPage/data/update", json=data)
    assert response.status_code == 200
    res = response.get_json()
    assert res["message"] == "會員資料更新成功"

def test_update_client_data_missing_field(client):
    data = {
        "cId": "C01",
        "email": "test01@mail.com",
        "phone": "0900000000",
        "sex": "男"
    }
    response = client.post("/clientPage/data/update", json=data)
    assert response.status_code == 400
    res = response.get_json()
    assert "缺少必要欄位" in res["message"]

def test_update_client_data_invalid_email(client):
    data = {
        "cId": "C01",
        "cName": "test01",
        "email": "test01",
        "phone": "0900000000",
        "sex": "男"
    }
    response = client.post("/clientPage/data/update", json=data)
    assert response.status_code == 400
    res = response.get_json()
    assert "電子郵件格式或長度錯誤" in res["message"]

def test_update_client_data_name_length(client):
    data = {
        "cId": "C01",
        "cName": "",
        "email": "test01@mail.com",
        "phone": "0900000000",
        "sex": "男"
    }
    response = client.post("/clientPage/data/update", json=data)
    assert response.status_code == 400
    res = response.get_json()
    assert "姓名長度必須" in res["message"]

# 測試 /clientPage/password/update 密碼更新 POST
def test_password_update_success(client):
    data = {"cId": "C01", "password": "For_Test_01"}
    response = client.post("/clientPage/password/update", json=data)
    assert response.status_code == 200
    res = response.get_json()
    assert res["message"] == "successfully modify password"
    assert res["cId"] == "C01"

def test_password_update_fail(client):
    data = {"cId": "C01", "password": "testtest"}
    response = client.post("/clientPage/password/update", json=data)
    assert response.status_code == 400
    res = response.get_json()
    assert "密碼格式錯誤" in res["message"]
