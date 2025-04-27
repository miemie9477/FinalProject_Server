#main.py

from flask import Flask, jsonify
from dbconfig.dbconnect import db, DB_URI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from routes.GoodDetail import GoodDetail_bp
from models.models import ClientFavorites
app = Flask(__name__)
app.register_blueprint(GoodDetail_bp)

# 設定 SQLAlchemy 連線
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True

# 初始化 SQLAlchemy
db.init_app(app)

@app.route("/")
def test_db():
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        return jsonify({
            "message": "Database connected",
            "result": result}), 200
    
    
    except Exception as e:
        return jsonify({
            "message": "Database connection failed",
            "error": str(e)
        })



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
