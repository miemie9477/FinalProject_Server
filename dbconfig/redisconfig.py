# 新版（在 Docker Compose 內部網路中是正確的）
import os
import redis

# 從環境變數中獲取 Redis 連線詳細資訊
# 如果環境變數未設定，則使用預設值（有利於在 Docker 外部進行本地測試）
redis_host = os.getenv('REDIS_HOST', 'localhost') # 預設為 'localhost'
redis_port = int(os.getenv('REDIS_PORT', 6379)) # 預設為 6379
redis_db = int(os.getenv('REDIS_DB', 0)) # 預設為 0

# 連接到 Redis
cache = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

# 可選：在啟動時進行快速連線檢查
try:
    cache.ping()
    print(f"成功連接到 Redis：{redis_host}:{redis_port}")
except redis.exceptions.ConnectionError as e:
    print(f"連接 Redis 錯誤於 {redis_host}:{redis_port}：{e}")
    # 在實際應用中，你可能希望更優雅地處理這個錯誤或直接退出
