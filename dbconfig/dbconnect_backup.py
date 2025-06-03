from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

DB_USERNAME = "sa"
DB_PASSWORD = "Root_123456"
DB_SERVER = "MIEMIE\\SQLEXPRESS"  
DB_NAME = "DB"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

# SQLAlchemy 的連線字串格式
DB_URI = (
    f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
    f"?driver={DB_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
)

# 初始化 SQLAlchemy
db = SQLAlchemy()
engine = create_engine(DB_URI)
