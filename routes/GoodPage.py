# app/routes/GoodPage.py

from flask import Blueprint, request, jsonify
from dbconfig.dbconnect import db
from models.models import Product

good_bp = Blueprint("good", __name__, url_prefix="/goodpage")

# /product 顯示所有商品，或根據 category 類別篩選，按 clickTimes 排序
@good_bp.route("", methods=["GET"])
def get_all_products():
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

    if category:
        query = query.filter(Product.category == category)

    # 預設按 clickTimes 排序
    products = query.order_by(Product.clickTimes.desc()).all()

    if not products:
        return jsonify({"message": "find no result"}), 404  # 找不到資料

    results = [{
        "pId": product.pId,
        "pName": product.pName,
        "brand": product.brand,
        "category": product.category,
        "price": float(product.price),
        "clickTimes": product.clickTimes,
        "review": product.review
    } for product in products]

    return jsonify({"results": results}), 200
