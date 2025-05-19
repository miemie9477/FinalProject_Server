from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import URL
from flask_sqlalchemy import SQLAlchemy
import urllib.parse  # MSSQL Windows 驗證方式（Trusted Connection）

# # 設定 Microsoft SQL Server 連線資訊
# DB_USERNAME = "miemie"
# DB_PASSWORD = ""
# DB_SERVER = "MIEMIE\\SQLEXPRESS"
# DB_NAME = "DB"

# # 建立 SQLAlchemy 連線字串
# DB_URI = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=no&Trusted_Connection=yes&TrustServerCertificate=yes"


params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MIEMIE\\SQLEXPRESS;"
    "DATABASE=DB;"
    "Trusted_Connection=yes;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)

DB_URI = "mssql+pyodbc:///?odbc_connect=" + params

db = SQLAlchemy()
engine = create_engine(DB_URI)