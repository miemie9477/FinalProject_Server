from flask import Response, Blueprint, jsonify, request
from models.models import Client, Client_Favorites, Good_Review, Product, Price_Now
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dbconfig.dbconnect import db
from dbconfig.redisconfig import cache
import json
import datetime
import os
import uuid
import jwt # 確保匯入 jwt
from dotenv import load_dotenv # 確保匯入 load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash # 確保匯入密碼工具
from utils.auth import token_required # 假設這是您自定義的 token_required 裝飾器

# 載入環境變數
load_dotenv()

# 從環境變數獲取 JWT 秘鑰
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

# --- GoodDetail Blueprint ---
goodDetail_bp = Blueprint("GoodDetail", __name__, url_prefix="/gooddetail")

# /product/<string:pId>
@goodDetail_bp.route("/product/<string:pId>", methods=["GET"])
def get_product_detail(pId):
    """
    根據商品 ID 獲取商品詳細資訊。
    此路由不需要 Token。
    """
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        product = Product.query.filter(Product.pId == pId).first()

        if not product:
            return jsonify({"error": "未找到資源"}), 404
        
        results = {
            "pId": product.pId,
            "pName": product.pName,
            "brand": product.brand,
            "category": product.category,
            "price": float(product.price),
            "review": float(product.review) if product.review is not None else None,
            "clickTimes": product.clickTimes
        }

        return Response(json.dumps({"results": results}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        print(f"SQLAlchemy 錯誤 (get_product_detail): {e}")
        return jsonify({"error": "資料庫操作錯誤"}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
# /priceNow/<string:pId>
@goodDetail_bp.route("/priceNow/<string:pId>", methods=["GET"])
def get_price_now(pId):
    """
    根據商品 ID 獲取商品目前的價格資訊。
    此路由不需要 Token。
    """
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400
        
        price_now_list = Price_Now.query.filter_by(pId=pId).all()
        if not price_now_list:
            return jsonify({"error": "未找到資源"}), 404
        
        results = [
                    {
                        "pId": item.pId,
                        "store": item.store,
                        "updateTime":item.updateTime.isoformat(),
                        "storePrice": float(item.storePrice),
                        "storeDiscount": item.storeDiscount,
                        "storeLink": item.storeLink
                    }for item in price_now_list
                ]
        
        return Response(json.dumps({"results": results}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        print(f"SQLAlchemy 錯誤 (get_price_now): {e}")
        return jsonify({"error": "資料庫操作錯誤"}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
# /productReview/<string:pId>
@goodDetail_bp.route("/productReview/<string:pId>", methods=["GET"])
def get_product_review(pId):
    """
    根據商品 ID 獲取商品的評論列表。
    此路由不需要 Token。
    """
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        get_review_list = Good_Review.query.filter_by(pId=pId).all()

        if not get_review_list:
            return jsonify({"error": "未找到資源"}), 404
        
        results = [
                    {
                        "pId": item.pId,
                        "userName": item.userName,
                        "date": item.date.isoformat() if item.date else None,
                        "rating": item.rating,
                        "reviewText": item.reviewText
                    }
                    for item in get_review_list
                ]
        return Response(json.dumps({"results": results}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        print(f"SQLAlchemy 錯誤 (get_product_review): {e}")
        return jsonify({"error": "資料庫操作錯誤"}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
# /click/<string:pId>
@goodDetail_bp.route("/click/<string:pId>", methods=["POST"]) 
def click(pId):
    """
    增加商品的點擊次數。
    此路由不需要 Token。
    """
    try:
        if not pId or not isinstance(pId, str): 
            return jsonify({"error": "請求參數錯誤"}), 400

        cache_key = f"click_times:{pId}"
        new_click_times = cache.incr(cache_key)

        return jsonify({
            "message": "點擊次數已累積",
            "new_click_times": int(new_click_times) 
        }), 200
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500


### 處理 Token 驗證後獲取 cId 的路由
'''
以下兩個路由 (track/id 和 track) 需要知道客戶 ID (cId)
因為它們會修改或查詢與該客戶相關的收藏資料。`token_required` 裝飾器應該會將已驗證的客戶資訊 (包含 cId) 傳遞給路由函數。
請確保您的 `utils.auth.token_required` 裝飾器會將解析後的 `payload` 或一個包含 `cId` 的字典賦值給 `request.user`
或直接作為參數傳入被裝飾的函數。** 我在下面的代碼中假設 `current_user` 是一個包含 `clientId` 鍵的字典。
'''

@goodDetail_bp.route("/track/id", methods=["POST"])
@token_required # 此路由需要 Token 驗證
def track_id(current_user): # current_user 由 token_required 傳入
    """
    檢查指定商品是否已被當前登入用戶追蹤（收藏）。
    需要 Token 驗證，cId 從 Token 中獲取。
    """
    try:
        cId = current_user['clientId'] # 從 Token 中獲取 cId
        data = request.get_json()
        pId = data.get('pId')

        # 驗證 pId 是否齊全且為字串類型
        if not pId or not isinstance(pId, str):
            return jsonify({'error': '請求參數錯誤'}), 400

        favorite = Client_Favorites.query.filter_by(cId=cId, pId=pId).first()

        if favorite:
            return jsonify({
                'cId': cId,
                'pId': pId,
                'status': 1,
                'message': '商品已在願望清單中'
            }), 200
        else:
            return jsonify({
                'cId': cId,
                'pId': pId,
                'status': 0,
                'message': '商品不在願望清單中'
            }), 200
            
    except SQLAlchemyError as e:
        print(f"SQLAlchemy 錯誤 (track_id): {e}")
        return jsonify({'error': '資料庫操作錯誤'}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500

@goodDetail_bp.route("/track", methods=["POST"])
@token_required # 此路由需要 Token 驗證
def toggle_track_status(current_user): # current_user 由 token_required 傳入
    """
    切換商品的追蹤（收藏）狀態：如果已收藏則取消，如果未收藏則加入。
    需要 Token 驗證，cId 從 Token 中獲取。
    """
    try:
        cId = current_user['clientId'] # 從 Token 中獲取 cId
        data = request.get_json()
        pId = data.get('pId')

        # 驗證 pId 是否齊全且為字串類型
        if not pId or not isinstance(pId, str):
            return jsonify({'error': '請求參數錯誤'}), 400

        favorite = db.session.get(Client_Favorites, {'cId': cId, 'pId': pId})

        if favorite:
            db.session.delete(favorite)
            new_status = 0
            message = "已取消追蹤"
        else:
            product_exists = Product.query.filter_by(pId=pId).first()
            if not product_exists:
                return jsonify({'error': f'無法追蹤，商品 ID {pId} 不存在'}), 404
            
            add_favorite = Client_Favorites(cId=cId, pId=pId)
            db.session.add(add_favorite)
            new_status = 1
            message = "已加入追蹤"
        
        db.session.commit()

        return jsonify({
            'message': message,
            'cId': cId,
            'pId': pId,
            'status': new_status
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"SQLAlchemy 錯誤 (toggle_track_status): {e}")
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"追蹤狀態切換時發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500

