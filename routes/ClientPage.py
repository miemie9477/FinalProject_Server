import re
from flask import Blueprint, Response, json, jsonify, request
from routes.GoodDetail import toggle_track_status  # 匯入函式
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from models.models import Client, Client_Favorites, Product # 假設 Product 模型可能在這裡被用到
# from routes.RegisterPage import is_valid_account, is_valid_password # 這些函式如果只用於註冊，可能無需在此導入
from sqlalchemy.orm import Session
from dbconfig.dbconnect import db
from werkzeug.security import generate_password_hash

# 從您的 utils.auth 導入 token_required
from utils.auth import token_required # 確保路徑正確

clientPage_bp = Blueprint("clientPage", __name__, url_prefix="/clientpage")

'''
 * 基本參數驗證：非字串型態& 齊全
 * 防止無效
'''

#-------------------------------------#
#       call /GoodDetail/track func   #
#-------------------------------------#
@clientPage_bp.route("/track", methods=["POST"])
@token_required
def clientpage_toggle_track():
    # 因為 toggle_track_status 函式是從 GoodDetail 導入的，
    # 如果它也需要 cId，並且期望 cId 在請求體中，您可能需要進行調整。
    # 理想情況下，toggle_track_status 也應該能從 request.user 獲取 cId，或者您將 cId 傳遞給它。
    # 這裡假設 toggle_track_status 內部會自行從 request 獲取或不需要 cId。
    return toggle_track_status()


@clientPage_bp.route("/trackList", methods=["GET"]) # 建議改成 GET，因為是獲取列表
@token_required # <-- 應用 token_required 裝飾器
def get_track_list():
    try:
        # 從 token_required 裝飾器附加的 request.user 中獲取 cId，更安全可靠
        cId = request.user['clientId']

        # Select * from Client_Favorites WHERE cId = ?
        track = Client_Favorites.query.filter(Client_Favorites.cId == cId).all()

        if not track:
            # 如果沒有追蹤資料，返回空列表，而不是 404，這樣前端處理更友好
            return jsonify({"results": []}), 200
        
        # 獲取追蹤商品詳細資訊
        result = []
        for item in track:
            product = db.session.get(Product, item.pId) # 假設 Product 模型已導入
            if product: # 確保商品存在
                result.append({
                    "cId": item.cId,
                    "pId": item.pId,
                    "pName": product.pName,
                    "brand": product.brand,
                    "category": product.category,
                    "price": float(product.price)
                    # 如果有圖片，也可以在這裡加入 imageUrl: product.imageUrl
                })
        
        return Response(json.dumps({"results": result}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        print(f"!!! SQLAlchemy Error Details: {e}")
        db.session.rollback() # 確保在錯誤時回滾
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        db.session.rollback() # 確保在錯誤時回滾
        return jsonify({'error': '伺服器內部錯誤'}), 500


# /client - 獲取會員基本資料
@clientPage_bp.route("/client", methods=["GET"]) # 建議改成 GET，因為是獲取資源
@token_required
def get_client_data(current_user):
    try:

        cId = current_user['clientId']
        print("cId:", cId)  # 確認 cId 是否正確
        client_data = Client.query.filter(Client.cId == cId).first()

        if not client_data:
            # 理論上，如果 Token 有效但找不到使用者，可能是數據不一致，可以考慮 500 或 404
            return jsonify({"error": "未找到會員資料"}), 404
        
        client_data_json = {
            "cName": client_data.cName,
            "account": client_data.account,
            "email": client_data.email,
            "phone": client_data.phone,
            "sex": client_data.sex,
            "birthday": client_data.birthday.strftime("%Y-%m-%d") if client_data.birthday else None # 格式化日期
        }
        
        return Response(json.dumps({"results": client_data_json}, ensure_ascii=False), mimetype='application/json')
        # return jsonify({'message': "OK"}), 200
    except SQLAlchemyError as e:
        print(f"!!! SQLAlchemy Error Details: {e}")
        db.session.rollback()
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        db.session.rollback()
        return jsonify({'error': '伺服器內部錯誤'}), 500


'''
update data欄位是否重複函式
這些輔助函式不需要 JWT 裝飾器，因為它們只在內部被調用。
'''
def is_duplicate_account(db_session: Session, account: str, exclude_id=None):
    query = db_session.query(Client).filter(Client.account == account)
    if exclude_id:
        query = query.filter(Client.cId != exclude_id)
    return query.first() is not None

def is_duplicate_email(db_session: Session, email: str, exclude_id=None):
    query = db_session.query(Client).filter(Client.email == email)
    if exclude_id:
        query = query.filter(Client.cId != exclude_id)
    return query.first() is not None

def is_duplicate_phone(db_session: Session, phone: str, exclude_id=None):
    query = db_session.query(Client).filter(Client.phone == phone)
    if exclude_id:
        query = query.filter(Client.cId != exclude_id)
    return query.first() is not None


@clientPage_bp.route("/data/update", methods=["POST"])
@token_required # <-- 應用 token_required 裝飾器
def update_client_data():
    try:
        # 從 request.user 中獲取 cId，確保更新的是當前登入用戶的資料
        cId = request.user['clientId']

        # 1. 檢查必要欄位
        data = request.get_json()
        required_fields = ["cName", "email", "phone", "sex"]
        missing = [field for field in required_fields if not (field in data and data[field] is not None)]
        if missing:
            return jsonify({"message": f"缺少必要欄位: {', '.join(missing)}"}), 400
        
        # 2. 獲取並驗證更新數據
        cName = data["cName"]
        email = data["email"]
        phone = data["phone"]
        sex = data["sex"]
        
        client = Client.query.filter_by(cId=cId).first()
        if not client:
            # 這種情況不應該發生，因為 cId 來自已驗證的 Token
            return jsonify({"message": "查無此會員或會員資料不一致"}), 404

        # Form Validation
        if not (1 <= len(cName) <= 30):
            return jsonify({"message": "姓名長度必須介於 1 到 30 個字元之間"}), 400
        
        # 更嚴謹的電子郵件正則表達式
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) or not (8 <= len(email) <= 64):
            return jsonify({"message": "電子郵件格式或長度錯誤 (需 8-64 字元)"}), 400
        if not re.match(r"^[0-9]{10}$", phone):
            return jsonify({"message": "電話號碼必須是 10 位數字"}), 400

        # 驗證重複，排除自己的 cId
        if is_duplicate_email(db.session, email, exclude_id=cId):
            return jsonify({"message": "Email 已存在"}), 400
        if is_duplicate_phone(db.session, phone, exclude_id=cId):
            return jsonify({"message": "電話已存在"}), 400

        # 更新
        client.cName = cName
        client.email = email
        client.phone = phone
        client.sex = sex
        
        db.session.commit()
        return jsonify({"message": "會員資料更新成功"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"!!! SQLAlchemy Error Details: {e}")
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    
    except Exception as e:
        db.session.rollback()
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500


@clientPage_bp.route("/password/update", methods=["POST"])
@token_required # <-- 應用 token_required 裝飾器
def password_update():
    try:
        # 從 request.user 中獲取 cId，確保更新的是當前登入用戶的密碼
        cId = request.user['clientId']

        data = request.get_json()
        new_password = data.get("password")

        if not new_password or not isinstance(new_password, str):
            return jsonify({"error": "請求參數錯誤，請提供新密碼"}), 400

        # 這裡需要確保 is_valid_password 函式是可用的，例如從 routes.RegisterPage 導入
        # 或者您可以直接在這裡實現密碼格式驗證
        from routes.RegisterPage import is_valid_password # 確保這個導入是有效的
        if not is_valid_password(new_password):
            return jsonify({"message": "密碼格式錯誤 (需 8-20 字元，包含大小寫字母及符號)"}), 400
            
        password_hash = generate_password_hash(new_password)

        client_to_update = Client.query.filter_by(cId=cId).first()
        if not client_to_update:
            # 同樣，這不應該發生在有有效 Token 的情況下
            return jsonify({"message": "查無此會員或會員資料不一致"}), 404
            
        client_to_update.password_hash = password_hash
        db.session.commit()

        return jsonify({"message": "成功修改密碼", "cId": cId}), 200

    except OperationalError as oe:
        db.session.rollback()
        print(f"!!! Operational Error Details: {oe}")
        return jsonify({'error': f'資料庫連線失敗或逾時: {str(oe)}'}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"!!! SQLAlchemy Error Details: {e}")
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500

    except Exception as e:
        db.session.rollback()
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': f'伺服器內部錯誤: {str(e)}'}), 500