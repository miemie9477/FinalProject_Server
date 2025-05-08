from flask import Blueprint, request, jsonify
from dbconfig.dbconnect import db
from models.models import Product  
from sqlalchemy import or_

home_bp = Blueprint("home", __name__, url_prefix="/homepage")

@home_bp.route("/product", methods=["GET"])
def get_products():
    category = request.args.get("category", None)  # 查詢參數 category
    sort = request.args.get("sort", "clickTimes")  # 默認按 clickTimes 排序

    # 基本參數驗證：非字串型態
    if (category and not isinstance(category, str)):
        return jsonify({"message": "Invalid request parameter"}), 400

    # 防止無效排序欄位
    allowed_sort_fields = {"clickTimes", "price", "review"}
    if sort not in allowed_sort_fields:
        return jsonify({"message": "Invalid request parameter"}), 400

    query = Product.query

    if category: # 如果有提供類別篩選
        query = query.filter(Product.category == category)

       
    # 預設按 clickTimes 排序
    products = query.order_by(Product.clickTimes.desc()).all()

    if not products:
        return jsonify({"message": "find no result"}), 404  # 找不到資料

    # 返回商品資料
    results = [{
        "pId": p.pId,
        "pName": p.pName,
        "brand": p.brand,
        "category": p.category,
        "price": float(p.price),
        "clickTimes": p.clickTimes,
        "review": p.review
    } for p in products]

    return jsonify({"results": results}), 200