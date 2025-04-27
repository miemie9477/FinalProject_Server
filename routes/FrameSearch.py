from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Unicode, Numeric, Integer, DateTime, Float, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pymssql://username:password@server/database'
db = SQLAlchemy(app)

# 定義產品資料表模型
class Product(db.Model):
    pId = db.Column(Unicode(8), primary_key=True)
    pName = db.Column(Unicode(50))
    brand = db.Column(Unicode(30))
    category = db.Column(Unicode(20))
    price = db.Column(Numeric(10, 2))
    clickTimes = db.Column(Integer)
    review = db.Column(Float)


# 定義 API 端點
@app.route('/search', methods=['POST'])
def search_product():
    try:
        data = request.get_json()
        keyword = data.get("keyword", "")

        if not keyword:
            return jsonify({"message": "Invalid request parameter"}), 400

        results = Product.query.filter(
            or_(
                Product.pName.ilike(f"%{keyword}%"),
                Product.brand.ilike(f"%{keyword}%")
            )
        ).all()

        if not results:
            return jsonify({"message": "find no result"}), 404

        response_data = [
            {
                "pid": product.pid,
                "pname": product.pname,
                "brand": product.brand,
                "category": product.category,
                "price": product.price,
                "clickTimes": product.clickTimes,
                "review": product.review
            } for product in results
        ]
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
