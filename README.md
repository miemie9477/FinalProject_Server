# 5/24 開發日誌 by mie
* suggest to put all validation func into *service\\*
* *GoodDetail.py*
    * 修改bp名稱(main也有一起改)
    * 把 */track/id* 加回來
* *clientPage.py*
    * 完成API
    * 有寫pytest & 手動測試(postman)
* 測試相關
> 我自己寫了一點簡單的測試，主要把200都測完，一小部分有測格式問題(沒有很多)
> 測試是我先寫txt, 後面叫chatgpt幫我生pytest(我沒有特別檢查過pytest)
```
# 測試覆蓋率
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
routes\ClientPage.py       129     40    69%   34, 41, 54-59, 69, 82, 86-91, 98-101, 156, 168, 174, 176, 187-194, 206, 220-231
```

# 專案規格
## Flask 後端專案

1. 命名規則以 "TagPath.py" ，記得分大小寫 (FrameSearch.py)

2. 我是使用SQLAlchemy，創建表格來輸出資料，model.py裡有寫好的資料表參數，FrameSearch中有範例

3. requirements.txt 有新增函式的話記得註解一下此函式作用

4. 如果該功能path較多，請在每個path註解功能

5. 寫法沒有硬性規定，能動就好ㄏ ，唯一要注意的是要抓的參數要跟model上資料表的一樣

## 使用的 Libraries
直接 pip install -r requirements.txt

## 專案目錄結構
```bash
app/
 └──│── routes/                     # 放不同路徑使用的api
    │     │── FrameSearch.py
    │     └──...
    │── models/                     # 定義 SQLAlchemy 模型
    │     └──model.py               # 各個資料表參數設定 （照Excel寫下來的）
    │── services/                   # 如果有自訂import services 放這邊
    │── dbconfig/  
    │     └──dbconnect.py           # 資料庫的連接config
    │── utils/                      # 工具函式（如驗證、加密等）有要做的話再說
    │── main.py                     # main file
    │── config.py                   # 設定檔 如果要提高server安全度，就要把敏感資訊改寫進config
    │── openapi.yaml                # api文件
    │── requirements.txt            # 依賴項（有要安裝任何libaries記得寫在這裡面，包括要安裝的版本）
```


## 目錄
--Tag
- [框架功能 (Frame)]
- [首頁功能 (HomePage)]
- [登入功能 (LoginPage)]
- [註冊功能 (RegisterPage)]
- [商品清單功能 (GoodPage)]
- [商品詳情功能 (GoodDetail)]
- [使用者個人頁面功能 (ClientPage)]
- [後台管理功能 (BackendPage)]


### 搜尋商品
- **介面**: POST /search
- **功能**: 根據關鍵字搜尋商品（使用 Like 搜尋商品名稱或品牌）
- **請求體**: 包含搜尋關鍵字
- **回應**: 傳回符合的商品列表

## 首頁功能 (HomePage)

### 取得商品列表
- **介面**: GET /product
- **功能**: 顯示所有或特定類別的商品（按點擊次數排序）
- **參數**:
 - category (可選): 商品類別
- **回應**: 返回商品列表

## 登入功能 (LoginPage)

### 使用者登入
- **介面**: POST /login
- **功能**: 驗證使用者登入訊息
- **請求體**: 包含帳號和密碼
- **驗證要求**:
 - account: 必填
 - password: 必填

## 註冊功能 (RegisterPage)

### 用戶註冊
- **介面**: POST /register
- **功能**: 新用戶註冊
- **驗證要求**:
 - 所有欄位必填
 - cName: 1-30字符
 - account: 8-20字符，需包含大小寫字母和符號
 - password: 8-20字符，需包含大小寫字母和符號
 - email: 8-20字符
 - phone: 10位數
 - birthday: 不能晚於當前日期
 - account、phone、email 不可重複
- **特殊處理**:
 - 需要郵箱驗證
 - 自動產生會員號碼（1位英文字母+7位數字）
 - 密碼加密存儲
 - 儲存登入狀態

## 商品清單功能 (GoodPage)

### 商品展示
- 與首頁共用 GET /product 接口
- 依點擊次數排序展示商品

## 商品詳情功能 (GoodDetail)

### 取得商品詳情
- **介面**: GET /product/{pId}
- **功能**: 獲取特定商品的詳細信息

### 取得商品價格
- **介面**: GET /priceNow/{pId}
- **功能**: 取得商品在各通路的價格訊息

### 商品評價
- **介面**: POST /productReview
- **功能**: 取得商品的評價訊息

### 點擊計數
- **介面**: POST /click/{pId}
- **功能**: 記錄商品頁面造訪次數

### 商品關注
- **介面**:
 - POST /track/id: 檢查商品關注狀態
 - POST /track/insert: 新增關注
 - POST /track/delete: 取消關注

## 使用者個人頁面功能 (ClientPage)

### 專注於商品管理
- **介面**: GET /track
- **功能**: 取得使用者所有關注的商品

### 使用者資訊管理
- **介面**:
 - POST /clientFavorites: 取得會員資料
 - POST /clientFavorites/update: 修改會員資料
- **可修改欄位**:
 - email
 - phone
 - sex
- **驗證要求**:
 - 所有欄位不可為空
 - 需符合原註冊要求
 - 修改的 email 和 phone 不可與其他使用者重複


## 錯誤碼說明

- 200: 請求成功
- 400: 請求參數錯誤
- 401: 未登入或權限不足
- 404: 未找到資源