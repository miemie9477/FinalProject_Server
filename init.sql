-- db/initdb/init.sql
-- 為 Docker 環境調整的 SQL Server 初始化腳本
-- 專為 SA 登入設計，並處理腳本可重復執行性

USE [master];
GO

-- 如果資料庫存在，先刪除它（用於開發環境的清理，請謹慎使用於生產環境）
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'DB')
BEGIN
    DROP DATABASE [DB];
END;
GO

-- 建立資料庫，明確指定 Docker 容器內的預設資料檔案路徑
-- 這通常是 /var/opt/mssql/data/
CREATE DATABASE [DB]
    CONTAINMENT = NONE
    ON PRIMARY
    ( NAME = N'DB', FILENAME = N'/var/opt/mssql/data/DB.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
    LOG ON
    ( NAME = N'DB_log', FILENAME = N'/var/opt/mssql/data/DB_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
    WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF;
GO

-- 確保切換到 'DB' 資料庫以執行後續的設定和物件創建
USE [DB];
GO

ALTER DATABASE [DB] SET COMPATIBILITY_LEVEL = 160;
GO

IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
BEGIN
    EXEC [DB].[dbo].[sp_fulltext_database] @action = 'enable';
END;
GO

ALTER DATABASE [DB] SET ANSI_NULL_DEFAULT OFF;
GO
ALTER DATABASE [DB] SET ANSI_NULLS OFF;
GO
ALTER DATABASE [DB] SET ANSI_PADDING OFF;
GO
-- 這裡刪除了一個多餘的 GO
ALTER DATABASE [DB] SET ANSI_WARNINGS OFF;
GO
ALTER DATABASE [DB] SET ARITHABORT OFF;
GO
ALTER DATABASE [DB] SET AUTO_CLOSE OFF;
GO
ALTER DATABASE [DB] SET AUTO_SHRINK OFF;
GO
ALTER DATABASE [DB] SET AUTO_UPDATE_STATISTICS ON;
GO
ALTER DATABASE [DB] SET CURSOR_CLOSE_ON_COMMIT OFF;
GO
ALTER DATABASE [DB] SET CURSOR_DEFAULT GLOBAL;
GO
ALTER DATABASE [DB] SET CONCAT_NULL_YIELDS_NULL OFF;
GO
ALTER DATABASE [DB] SET NUMERIC_ROUNDABORT OFF;
GO
ALTER DATABASE [DB] SET QUOTED_IDENTIFIER OFF;
GO
ALTER DATABASE [DB] SET RECURSIVE_TRIGGERS OFF;
GO
ALTER DATABASE [DB] SET DISABLE_BROKER;
GO
ALTER DATABASE [DB] SET AUTO_UPDATE_STATISTICS_ASYNC OFF;
GO
ALTER DATABASE [DB] SET DATE_CORRELATION_OPTIMIZATION OFF;
GO
ALTER DATABASE [DB] SET TRUSTWORTHY OFF;
GO
ALTER DATABASE [DB] SET ALLOW_SNAPSHOT_ISOLATION OFF;
GO
ALTER DATABASE [DB] SET PARAMETERIZATION SIMPLE;
GO
ALTER DATABASE [DB] SET READ_COMMITTED_SNAPSHOT OFF;
GO
ALTER DATABASE [DB] SET HONOR_BROKER_PRIORITY OFF;
GO
ALTER DATABASE [DB] SET RECOVERY SIMPLE;
GO
ALTER DATABASE [DB] SET MULTI_USER;
GO
ALTER DATABASE [DB] SET PAGE_VERIFY CHECKSUM;
GO
ALTER DATABASE [DB] SET DB_CHAINING OFF;
GO
ALTER DATABASE [DB] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF );
GO
ALTER DATABASE [DB] SET TARGET_RECOVERY_TIME = 60 SECONDS;
GO
ALTER DATABASE [DB] SET DELAYED_DURABILITY = DISABLED;
GO
ALTER DATABASE [DB] SET ACCELERATED_DATABASE_RECOVERY = OFF;
GO
ALTER DATABASE [DB] SET QUERY_STORE = ON;
GO
ALTER DATABASE [DB] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON);
GO

-- 由於您使用 SA 登入，不需要額外建立 root 登入和使用者
-- --- 表格結構定義 (CREATE TABLE) ---
USE [DB];
GO

-- 在創建表格前，先檢查並刪除它們（從從屬關係最弱的開始刪除，避免外鍵衝突）
-- 外鍵約束通常是最後添加的，所以刪除時要先刪除依賴的表，再刪除被依賴的表。
IF OBJECT_ID('dbo.Client_Favorites', 'U') IS NOT NULL DROP TABLE dbo.Client_Favorites;
IF OBJECT_ID('dbo.Good_Review', 'U') IS NOT NULL DROP TABLE dbo.Good_Review;
IF OBJECT_ID('dbo.Price_History', 'U') IS NOT NULL DROP TABLE dbo.Price_History;
IF OBJECT_ID('dbo.Price_Now', 'U') IS NOT NULL DROP TABLE dbo.Price_Now;
IF OBJECT_ID('dbo.Client', 'U') IS NOT NULL DROP TABLE dbo.Client; -- Client 表可能被 Client_Favorites 引用，所以先刪除 Favorites
IF OBJECT_ID('dbo.Product', 'U') IS NOT NULL DROP TABLE dbo.Product; -- Product 表被多個表引用，所以先刪除引用它的表
GO

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO

-- 建立 Product 資料表
CREATE TABLE [dbo].[Product](
    [pId] [nvarchar](8) NOT NULL,
    [pName] [nvarchar](50) NULL,
    [brand] [nvarchar](30) NULL,
    [category] [nvarchar](20) NULL,
    [price] [decimal](10, 2) NULL,
    [clickTimes] [int] NULL,
    [review] [float] NULL,
CONSTRAINT [PK_Product] PRIMARY KEY CLUSTERED
(
    [pId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY];
GO

-- 建立 Client 資料表
CREATE TABLE [dbo].[Client](
    [cId] [nvarchar](8) NOT NULL,
    [cName] [nvarchar](30) NULL,
    [account] [nvarchar](20) NULL,
    [password] [varchar](255) NULL,
    [email] [nvarchar](64) NULL,
    [phone] [nvarchar](10) NULL,
    [sex] [nvarchar](14) NULL,
    [birthday] [datetime] NULL,
CONSTRAINT [PK_Client] PRIMARY KEY CLUSTERED
(
    [cId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY];
GO

-- 建立 Client_Favorites 資料表
CREATE TABLE [dbo].[Client_Favorites](
    [cId] [nvarchar](8) NOT NULL,
    [pId] [nvarchar](8) NOT NULL,
CONSTRAINT [PK_Client_favorites] PRIMARY KEY CLUSTERED
(
    [cId] ASC,
    [pId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY];
GO

-- 建立 Good_Review 資料表
CREATE TABLE [dbo].[Good_Review](
    [pId] [nvarchar](8) NOT NULL,
    [date] [datetime] NOT NULL,
    [userName] [nvarchar](30) NULL,
    [rating] [float] NULL,
    [reviewText] [nvarchar](max) NULL,
CONSTRAINT [PK_GoodReview] PRIMARY KEY CLUSTERED
(
    [pId] ASC,
    [date] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY];
GO

-- 建立 Price_History 資料表
CREATE TABLE [dbo].[Price_History](
    [pId] [nvarchar](8) NOT NULL,
    [updateTime] [datetime] NOT NULL,
    [prePrice] [numeric](10, 2) NULL,
    [storeName] [nvarchar](50) NULL,
CONSTRAINT [PK_Price_History] PRIMARY KEY CLUSTERED
(
    [pId] ASC,
    [updateTime] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY];
GO

-- 建立 Price_Now 資料表
CREATE TABLE [dbo].[Price_Now](
    [pId] [nvarchar](8) NOT NULL,
    [updateTime] [datetime] NOT NULL,
    [store] [nvarchar](50) NULL,
    [storePrice] [numeric](10, 2) NULL,
    [storeDiscount] [nvarchar](200) NULL,
    [storeLink] [nvarchar](200) NULL,
CONSTRAINT [PK_Price_Now_1] PRIMARY KEY CLUSTERED
(
    [pId] ASC,
    [updateTime] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY];
GO

--- 資料插入 (INSERT INTO) ---
-- 在插入資料前，清空表格，以避免主鍵衝突（按照外鍵關係，從被依賴的表開始清空）
DELETE FROM [dbo].[Client_Favorites];
DELETE FROM [dbo].[Good_Review];
DELETE FROM [dbo].[Price_History];
DELETE FROM [dbo].[Price_Now];
DELETE FROM [dbo].[Client];
DELETE FROM [dbo].[Product];
GO

INSERT [dbo].[Client] ([cId], [cName], [account], [password], [email], [phone], [sex], [birthday]) VALUES (N'C01', N'test001', N'Test_0001', N'pbkdf2:sha256:600000$f3BZAQb56f7CoLYd$5a6807d6fb4018c4a9e701ae1e69614bd745f38f082d07fbaddc756a8102549f', N'test01@mail.com', N'0912345678', N'男', CAST(N'1905-06-20T00:00:00.000' AS DateTime));
INSERT [dbo].[Client] ([cId], [cName], [account], [password], [email], [phone], [sex], [birthday]) VALUES (N'C02', N'test02', N'Test02', N'test02', N'test02@mail.com', N'0932165498', N'女', CAST(N'1905-05-22T00:00:00.000' AS DateTime));
INSERT [dbo].[Client] ([cId], [cName], [account], [password], [email], [phone], [sex], [birthday]) VALUES (N'C03', N'test03', N'Test03', N'test03', N'test03@mail.com', N'0987654321', N'女', CAST(N'1905-05-12T00:00:00.000' AS DateTime));
GO
INSERT [dbo].[Client_Favorites] ([cId], [pId]) VALUES (N'C01', N'P01');
INSERT [dbo].[Client_Favorites] ([cId], [pId]) VALUES (N'C01', N'P02');
INSERT [dbo].[Client_Favorites] ([cId], [pId]) VALUES (N'C01', N'P04');
INSERT [dbo].[Client_Favorites] ([cId], [pId]) VALUES (N'C02', N'P02');
INSERT [dbo].[Client_Favorites] ([cId], [pId]) VALUES (N'C03', N'P03');
GO
INSERT [dbo].[Good_Review] ([pId], [date], [userName], [rating], [reviewText]) VALUES (N'P01', CAST(N'2025-04-22T18:25:40.000' AS DateTime), N'waston', 5, N'Ｎice');
INSERT [dbo].[Good_Review] ([pId], [date], [userName], [rating], [reviewText]) VALUES (N'P01', CAST(N'2025-04-22T18:25:42.000' AS DateTime), N'waston', 1, N'爛死了');
GO
INSERT [dbo].[Price_History] ([pId], [updateTime], [prePrice], [storeName]) VALUES (N'P01', CAST(N'1901-02-04T00:00:00.000' AS DateTime), CAST(2021.00 AS Numeric(10, 2)), N'康氏美');
INSERT [dbo].[Price_History] ([pId], [updateTime], [prePrice], [storeName]) VALUES (N'P02', CAST(N'1900-09-13T00:00:00.000' AS DateTime), CAST(2021.00 AS Numeric(10, 2)), N'屈臣氏');
INSERT [dbo].[Price_History] ([pId], [updateTime], [prePrice], [storeName]) VALUES (N'P03', CAST(N'1900-10-17T00:00:00.000' AS DateTime), CAST(2021.00 AS Numeric(10, 2)), N'康氏美');
GO
INSERT [dbo].[Price_Now] ([pId], [updateTime], [store], [storePrice], [storeDiscount], [storeLink]) VALUES (N'P01', CAST(N'2025-04-22T18:25:40.000' AS DateTime), N'cosme', CAST(2500.00 AS Numeric(10, 2)), N'無', N'0');
INSERT [dbo].[Price_Now] ([pId], [updateTime], [store], [storePrice], [storeDiscount], [storeLink]) VALUES (N'P01', CAST(N'2025-04-22T18:25:42.000' AS DateTime), N'watson', CAST(2021.00 AS Numeric(10, 2)), N'開架彩妝88折', N'0');
INSERT [dbo].[Price_Now] ([pId], [updateTime], [store], [storePrice], [storeDiscount], [storeLink]) VALUES (N'P01', CAST(N'2025-04-22T18:25:43.000' AS DateTime), N'poya', CAST(2021.00 AS Numeric(10, 2)), N'兩件5折', N'0');
GO
INSERT [dbo].[Product] ([pId], [pName], [brand], [category], [price], [clickTimes], [review]) VALUES (N'P01', N'Hair Recipe化妝品_臉部彩妝', N'Hair Recipe髮的食譜', N'化妝品_臉部彩妝', CAST(399.00 AS Decimal(10, 2)), 6, 4.9);
INSERT [dbo].[Product] ([pId], [pName], [brand], [category], [price], [clickTimes], [review]) VALUES (N'P02', N'Dove多芬 化妝品_眼眉彩妝_眼影', N'Dove多芬', N'化妝品_眼眉彩妝_眼影', CAST(255.00 AS Decimal(10, 2)), 0, 5);
INSERT [dbo].[Product] ([pId], [pName], [brand], [category], [price], [clickTimes], [review]) VALUES (N'P03', N'head&shoulders海倫仙度絲 去屑洗髮乳 檸檬清爽', N'head&shoulders海倫仙度絲', N'化妝品_唇部彩妝_唇膏', CAST(289.00 AS Decimal(10, 2)), 0, 5);
INSERT [dbo].[Product] ([pId], [pName], [brand], [category], [price], [clickTimes], [review]) VALUES (N'P04', N'head&shoulders臉部保養_卸妝_卸妝油&乳&水', N'head&shoulders海倫仙度絲', N'臉部保養_卸妝_卸妝油&乳&水', CAST(289.00 AS Decimal(10, 2)), 0, 5);
INSERT [dbo].[Product] ([pId], [pName], [brand], [category], [price], [clickTimes], [review]) VALUES (N'P05', N'head&shoulders臉部保養_保養', N'head&shoulders海倫仙度絲', N'臉部保養_保養', CAST(289.00 AS Decimal(10, 2)), 0, 5);
GO

--- 外鍵約束 (FOREIGN KEY CONSTRAINTS) ---
USE [DB];
GO

ALTER TABLE [dbo].[Client_Favorites] WITH CHECK ADD CONSTRAINT [FK_Client_Favorites_Client1] FOREIGN KEY([cId])
REFERENCES [dbo].[Client] ([cId]);
GO
ALTER TABLE [dbo].[Client_Favorites] CHECK CONSTRAINT [FK_Client_Favorites_Client1];
GO
ALTER TABLE [dbo].[Client_Favorites] WITH CHECK ADD CONSTRAINT [FK_Client_favorites_Product] FOREIGN KEY([pId])
REFERENCES [dbo].[Product] ([pId]);
GO
ALTER TABLE [dbo].[Client_Favorites] CHECK CONSTRAINT [FK_Client_favorites_Product];
GO
ALTER TABLE [dbo].[Good_Review] WITH CHECK ADD CONSTRAINT [FK_GoodReview_Product] FOREIGN KEY([pId])
REFERENCES [dbo].[Product] ([pId]);
GO
ALTER TABLE [dbo].[Good_Review] CHECK CONSTRAINT [FK_GoodReview_Product];
GO
ALTER TABLE [dbo].[Price_History] WITH CHECK ADD CONSTRAINT [FK_Price_History_Product] FOREIGN KEY([pId])
REFERENCES [dbo].[Product] ([pId]);
GO
ALTER TABLE [dbo].[Price_History] CHECK CONSTRAINT [FK_Price_History_Product];
GO
ALTER TABLE [dbo].[Price_Now] WITH CHECK ADD CONSTRAINT [FK_Price_Now_Product] FOREIGN KEY([pId])
REFERENCES [dbo].[Product] ([pId]);
GO
ALTER TABLE [dbo].[Price_Now] CHECK CONSTRAINT [FK_Price_Now_Product];
GO

-- 最後，確保回到 master 資料庫並設定為讀寫模式
USE [master];
GO
ALTER DATABASE [DB] SET READ_WRITE;
GO