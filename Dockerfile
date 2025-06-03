# 使用官方 Python 映像（瘦身版）
FROM python:3.10-slim

# 安裝 pyodbc 依賴與 SQL Server ODBC Driver 17
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc g++ curl gnupg2 unixodbc unixodbc-dev libssl-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製需求檔與安裝套件
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案
COPY . .

# 開放 Flask port
EXPOSE 5000

# 設定環境變數讓 Flask 運行
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# 執行 Flask
CMD ["flask", "run"]
