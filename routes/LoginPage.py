from flask import Blueprint, request, jsonify
from dbconfig.dbconnect import db
from models.models import Client # 假設您的模型名稱是 Client
from sqlalchemy import collate
from werkzeug.security import check_password_hash
login_bp = Blueprint('login', __name__, url_prefix="/loginpage")

@login_bp.route("/login", methods=["POST"])
def login():
    """
    登入功能 API 端點 (使用 SQLAlchemy ORM)
    """
    data = request.get_json()

    try:
        # 1. 從請求中獲取 JSON 數據並提取欄位
        account = data.get("account")
        password = data.get("password") # 獲取前端提供的原始密碼

        # 2. 檢查 account 和 password 是否提供
        if not account or not password:
            return jsonify({"message": "帳號和密碼都是必填項"}), 400

        # 3. (可選) 驗證長度 (如果需要，可以保留)
        if not (8 <= len(account) <= 20 and 8 <= len(password) <= 20):
             return jsonify({"message": "帳號或密碼長度不符 (應為 8-20 字元)"}), 400

        # 4. 使用 SQLAlchemy 查找使用者 (帳號區分大小寫)
        user = db.session.query(Client).filter(
            Client.account.collate('Latin1_General_CS_AS') == account
        ).first() # 獲取第一筆符合的使用者物件

        # 5. 驗證使用者是否存在以及密碼是否匹配
        if user and check_password_hash(user.password_hash, password): 
            # 使用者存在且 (不安全的) 密碼比對成功
            print(f"使用者 '{account}' 登入成功 (ORM)。用戶ID: {user.cId}")
            return jsonify({
                "message": "登入成功",
                "clientId": user.cId,    # 從 user 物件獲取 cId
                "clientName": user.cName # 從 user 物件獲取 cName
            }), 200
        else:
            # 使用者不存在或密碼錯誤
            print(f"使用者 '{account}' 登入失敗：帳號或密碼錯誤 (ORM)。")
            return jsonify({"message": "帳號或密碼錯誤"}), 401 # 401 Unauthorized

    except Exception as e:
        # 捕捉查詢或其他過程中可能發生的錯誤
        print(f"登入過程中發生未預期錯誤: {e}")
        # 建議回滾，以防萬一 Session 中有意外變更
        db.session.rollback() 
        return jsonify({"message": f"登入過程中發生錯誤: {e}"}), 500

