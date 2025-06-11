import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

DB_USERNAME = os.getenv("DB_USERNAME", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Root_123456")
DB_SERVER = os.getenv("DB_SERVER", "localhost")  # SQL Server instance name
DB_PORT    = os.getenv("DB_PORT", "1433")
DB_NAME    = os.getenv("DB_NAME", "DB")  # Database name
DB_DRIVER  = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

if DB_PORT:
    DB_HOST = f"{DB_SERVER},{DB_PORT}"
else:
    DB_HOST = DB_SERVER  # 本機使用 instance name，不加 port

DB_URI = (
    f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    f"?driver={DB_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
)
print(f"Connecting to database at {DB_URI}")

db = SQLAlchemy()
engine = create_engine(DB_URI)


