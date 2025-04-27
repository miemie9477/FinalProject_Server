from flask import Response, Blueprint, jsonify, request
from models.models import ClientFavorites, GoodReview, Product, PriceNow
from sqlalchemy.exc import SQLAlchemyError
from dbconfig.dbconnect import db
import json

GoodDetail_bp = Blueprint("GoodDetail", __name__, url_prefix="/GoodDetail")

'''
目前版本只有簡單測輸入正確值
學習寫測試中
'''

# /product/<string:pId>
@GoodDetail_bp.route("/product/<string:pId>", methods=["GET"])
def get_product_detail(pId):
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        # select * from Product where pId=?
        product = Product.query.filter(Product.pId == pId).first()

        if not product:
            return jsonify({"error": "未找到資源"}), 404
        
        result = {
            "pId": product.pId,
            "pName": product.pName,
            "brand": product.brand,
            "category": product.category,
            "price": float(product.price),
            "review": float(product.review) if product.review is not None else None,
            "clickTimes": product.clickTimes
        }

        # ensure_ascii=False：讓中文顯示正常
        return Response(json.dumps({"results": result}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

# /priceNow/<string:pId>
@GoodDetail_bp.route("/priceNow/<string:pId>", methods=["GET"])
def get_price_now(pId):
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400
        
        price_now_list = PriceNow.query.filter_by(pId=pId).all()
        if not price_now_list:
            return jsonify({"error": "未找到資源"}), 404
        
        # datetime 類型，不能直接丟進 json.dumps()
        result = [
                    {
                        "pId": item.pId,
                        "store": item.store,
                        "updateTime":item.updateTime.isoformat(),
                        "storePrice": float(item.storePrice),
                        "storeDiscount": item.storeDiscount,
                        "storeLink": item.storeLink
                    }for item in price_now_list
                ]
        
        return Response(json.dumps({"results": result}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

# /productReview/<string:pId>
@GoodDetail_bp.route("/productReview/<string:pId>", methods=["GET"])
def get_product_review(pId):
    try:
        if not pId:
            return jsonify({"error": "請求參數錯誤"}), 400

        get_review_list = GoodReview.query.filter_by(pId=pId).all()

        if not get_review_list:
            return jsonify({"error": "未找到資源"}), 404
        
        # The date needs to be converted into date format.
        result = [
                    {
                        "pId": item.pId,
                        "userName": item.userName,
                        "date": item.date.isoformat() if item.date else None,
                        "rating": item.rating,
                        "reviewText": item.reviewText
                    }
                    for item in get_review_list
                ]
        return Response(json.dumps({"results": result}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500

# /click/<string:pId>
@GoodDetail_bp.route("/click/<string:pId>", methods=["POST"])
def click(pId):
    try:
        if not pId:
            return jsonify({"error": "請求參數錯誤"}), 400

        # 先把舊的clicktimes從Product撈出來
        origin_click_times = Product.query.with_entities(Product.pId, Product.clickTimes).filter_by(pId=pId).first()

        if not origin_click_times:
            return jsonify({"error": "未找到資源"}), 404

        # 數值加1後 Update clicktimes 欄位
        update_click_times = origin_click_times.clickTimes + 1
        Product.query.filter_by(pId=pId).update({"clickTimes": update_click_times})
        db.session.commit()

        new = Product.query.with_entities(Product.pId, Product.clickTimes).filter_by(pId=pId).first()
        return jsonify({
            "message": "點擊次數已更新",
            "clickTimes": new.clickTimes
        }), 200
    
    except SQLAlchemyError as e:
        # 資料庫操作過程中出錯，就回滾（rollback()）以避免半寫入的狀況
        db.session.rollback()
        return jsonify({str(e)}), 500
    finally:
        db.session.remove()

@GoodDetail_bp.route("/track/id", methods=["POST"])
def track_id():
    try:
        data = request.get_json()
        cId = data.get('cId')
        pId = data.get('pId')

        # 驗證參數是否齊全
        if not cId or not pId:
            return jsonify({'error': '請求參數錯誤'}), 400

        # 查詢是否已關注
        favorite = ClientFavorites.query.filter_by(cId=cId, pId=pId).first()

        # 有關注，status = 1
        if favorite:
            return jsonify({
                'cId': cId,
                'pId': pId,
                'status': 1
            }), 200
        else:
            return jsonify({
                'cId': cId,
                'pId': pId,
                'status': 0
            }), 200
        
    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500

'''
下面這兩個以後可以考慮整合(用status管理，切換狀態)
'''
@GoodDetail_bp.route("/track/insert", methods=["POST"])
def track_insert():
    try:
        data = request.get_json()
        cId = data.get('cId')
        pId = data.get('pId')

        # 驗證參數是否齊全
        if not cId or not pId:
            return jsonify({'error': '請求參數錯誤'}), 400
        
        add_favorite = ClientFavorites(cId=cId, pId=pId)

        # 加入 session 並提交
        db.session.add(add_favorite)
        db.session.commit()

        
        # 回傳成功訊息
        
        return jsonify({'message': 'success'}), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({str(e)}), 500


@GoodDetail_bp.route("/track/delete", methods=["POST"])
def track_delete():
    try:
        data = request.get_json()

        cId = data.get('cId')
        pId = data.get('pId')

        if not cId or not pId:
            return jsonify({'message': '請求參數錯誤'}), 400

        favorite = ClientFavorites.query.filter_by(cId=cId, pId=pId).first()

        if not favorite:
            return jsonify({'message': '找不到資源'}), 404

        db.session.delete(db.session.merge(favorite))
        db.session.commit()
        
        return jsonify({'message': 'success'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({str(e)}), 500