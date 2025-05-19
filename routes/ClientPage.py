import re
from flask import Blueprint, Response, json, jsonify, request
from routes.GoodDetail import toggle_track_status  # 匯入函式
from sqlalchemy.exc import SQLAlchemyError
from models.models import Client, Client_Favorites
from routes.RegisterPage import is_valid_account, is_valid_password
from flasgger import swag_from
clientPage_bp = Blueprint("clientPage", __name__)

'''
 * 基本參數驗證：非字串型態& 齊全
 * 防止無效
'''

#-------------------------------------#
#      call /GoodDetail/track func    #
#-------------------------------------#
@clientPage_bp.route("/track", methods=["POST"])
def clientpage_toggle_track():
    return toggle_track_status()  # 重用邏輯


@clientPage_bp.route("/trackList", methods=["POST"])
def get_track_list():
    try:
        data = request.get_json()
        cId = data.get('cId')

        # 基本參數驗證：非字串型態& 齊全
        if not cId or not isinstance(cId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        # Select * from Client_Favorites WHERE cId = ?
        track = Client_Favorites.query.filter(Client_Favorites.cId == cId)

        # 防止無效
        if not track:
            return jsonify({"error": "未找到資源"}), 404
        
        # Track might be an array of objects
        # Using for loop to get data
        result = [
                    {
                        "cId": item.cId,
                        "pId": item.pId
                    }
                    for item in track
                ]
        return Response(json.dumps({"results": result}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        print(f"!!! SQLAlchemy Error Details: {e}")
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500

# /client
@clientPage_bp.route("/client", methods=["POST"])
def get_client_data():
    try:
        data = request.get_json()
        cId = data.get('cId')
        if not cId or not isinstance(cId, str):
            return jsonify({"error": "請求參數錯誤"})
        
        client_data = Client.query.filter(Client.cId == cId).first()

        if not client_data:
            return jsonify({"error": "未找到資源"}), 404
        
        return Response(json.dumps({"results": client_data}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500

    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500


@clientPage_bp.route("/client/update", methods=["POST"])
def update_client_data():
    try:
        '''
        * 需登入，account + birthday + sex 不可修改
        * 用textfield方式呈現，default value 為原本會員資料
            * 密碼不需要放default value
            * textfeild value不可為空值
        * 送出後要檢查
            * 所有欄位皆為required
            * cName: 1<=長度<=30
            * account:需含大小寫、符號、8<=長度<=20
            * password: 需含大小寫、符號、8<=長度<=20
            * email: >=8,<=20
            * phone: 長度 == 10
            * birthday: 日期<=現在日期
            * account、password、phone、email皆不可重複
        '''

        # 1. 檢查必要欄位
        data = request.get_json()
        required_fields = ["cName", "account", "password", "email", "phone", "sex", "birthday"]
        missing = [field for field in required_fields if not (field in data and data[field] is not None)]
        if missing:
            return jsonify({"message": f"缺少必要欄位: {', '.join(missing)}"}), 400
        

        # 2. 解析欄位值 (與之前相同)
        cId = data["cId"]
        cName = data["cName"]
        account = data["account"]
        password = data["password"]
        email = data["email"]
        phone = data["phone"]
        sex = data["sex"]
        birthday_str = data["birthday"]


        # --- 輔助函數 (驗證、產生ID) ---

        if not (1 <= len(cName) <= 30):
            return jsonify({"message": "姓名長度必須介於 1 到 30 個字元之間"}), 400
        # From Register import func: is_valid_account, is_valid_password
        if not is_valid_account(account):
            return jsonify({"message": "帳號格式錯誤 (需 8-20 字元，包含大小寫字母及符號)"}), 400
        if not is_valid_password(password):
             return jsonify({"message": "密碼格式錯誤 (需 8-20 字元，包含大小寫字母及符號)"}), 400
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or not (8 <= len(email) <= 64):
            return jsonify({"message": "電子郵件格式或長度錯誤 (需 8-64 字元)"}), 400
        if not re.match(r"^[0-9]{10}$", phone):
            return jsonify({"message": "電話號碼必須是 10 位數字"}), 400

    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500
    
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500