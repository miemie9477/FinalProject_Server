# db/Dockerfile
# FROM mcr.microsoft.com/mssql/server:2022-latest

# 將你的 init.sql 檔案複製到容器的根目錄
# COPY ../init.sql /init.sql

# 這是最直接且能解決時序問題的 CMD 腳本：
# 1. 在背景啟動 SQL Server 服務。
# 2. 等待一個固定的時間 (例如 30 秒)，讓 SQL Server 啟動。
# 3. 執行你的 init.sql 腳本。
# 4. 保持 SQL Server 主進程運行，確保容器不會退出。

# 測試執行docker up --build，建置過程大概要數分鐘，所以這邊sleep掛220秒，看起來應該是OK
# CMD /bin/bash -c "/opt/mssql/bin/sqlservr & \
#     echo '等待 SQL Server 啟動中，請稍候 30 秒...' ; \
#     sleep 220 ; \
#     echo '執行 init.sql...' ; \
#     /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P 'Root_123456' -C -i /init.sql ; \
#     wait"


# db/Dockerfile
FROM mcr.microsoft.com/mssql/server:2022-latest

# 將你的 init.sql 檔案複製到 SQL Server 官方映像檔的初始化目錄
COPY ../init.sql /docker-entrypoint-initdb.d/init.sql

# 移除你自定義的 CMD 腳本。
# 官方映像檔的 ENTRYPOINT 會自動啟動 SQL Server 並執行 /docker-entrypoint-initdb.d 中的腳本。
# 不需要額外的 CMD 腳本來等待和執行 init.sql。