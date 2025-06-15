from flask import Blueprint, request, jsonify
from sqlalchemy import distinct, or_
from dbconfig.dbconnect import db
from models.models import Product

frame_bp = Blueprint("frame", __name__, url_prefix="/frame")

# /frame/search 搜尋商品 (使用 SQLAlchemy ORM)
@frame_bp.route("/search", methods=["POST"])
def search_products():

    # 取得 keyword，如果沒有提供則預設為空字串，並去除前後空白
    data = request.get_json()
    keyword = data.get("keyword", "").strip() 
    
    try:
        products_to_return = [] # 初始化最終要回傳的產品列表

        if keyword:
            # --- 情況一：有提供搜尋關鍵字 ---
            # 建立一個基礎查詢，選取所有 Product 物件
            base_query = Product.query
            
            # 添加篩選條件：pName 或 brand 包含該 keyword
            found_products_raw = base_query.filter(
                or_(
                    Product.pName.ilike(f"%{keyword}%"),
                    Product.brand.ilike(f"%{keyword}%")
                )
            ).all()

            # 對結果進行去重 (基於 pId)，並轉換成字典格式
            # 使用一個集合 (set) 來追蹤已經添加的 pId，確保唯一性
            seen_pids = set()
            for p in found_products_raw:
                if p.pId not in seen_pids:
                    products_to_return.append({
                        "pId": p.pId,
                        "pName": p.pName,
                        "brand": p.brand,
                        "category": p.category,
                        "price": float(p.price) if p.price is not None else None,
                        "clickTimes": p.clickTimes,
                        "review": p.review
                    })
                    seen_pids.add(p.pId)
            
            # --- 判斷搜尋結果 (針對有 keyword 的情況) ---
            if not products_to_return:
                # 如果有關鍵字但沒有找到任何結果，返回 404 狀態碼和特定的訊息
                return jsonify({
                    "results": "找不到符合條件的商品",
                }), 401

        else:
            # --- 情況二：沒有提供搜尋關鍵字 (keyword 為空字串) ---
            # 回傳所有 Product 物件的完整資料
            all_products = Product.query.all() 
            
            # 將完整的 Product 物件列表轉換為字典格式
            for p in all_products:
                products_to_return.append({
                    "pId": p.pId,
                    "pName": p.pName,
                    "brand": p.brand,
                    "category": p.category,
                    "price": float(p.price) if p.price is not None else None,
                    "clickTimes": p.clickTimes,
                    "review": p.review
                })

        # --- 統一回傳結果 ---
        return jsonify({"results": products_to_return}), 200

    except Exception as e:
        # 捕捉並列印錯誤，便於開發除錯。在生產環境應使用日誌系統。
        print(f"搜尋商品時發生錯誤: {e}")
        # 返回一個通用的伺服器內部錯誤訊息給前端
        return jsonify({"message": "伺服器內部錯誤，搜尋失敗"}), 500