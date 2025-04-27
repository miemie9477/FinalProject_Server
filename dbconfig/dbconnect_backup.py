#dbconnect.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import pyodbc
# 設定 Microsoft SQL Server 連線資訊
DB_USERNAME = "miemie"
DB_PASSWORD = ""
DB_SERVER = "MIEMIE\SQLEXPRESS"
DB_NAME = "DB"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

# 建立 SQLAlchemy 連線字串
# DB_URI = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}@{DB_DRIVER}"


DB_URI = (
    f"DRIVER-{{{DB_DRIVER}}};"                  
    f"SERVER-{DB_SERVER};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USERNAME};"
    f"PWD={DB_PASSWORD}"
    f"&TrustServerCertificate=yes"
)

conn = pyodbc.connect(DB_URI, autocommit=False)
cursor = conn.cursor()
print("OK");
# 初始化 SQLAlchemy
db = SQLAlchemy()
engine = create_engine(DB_URI)