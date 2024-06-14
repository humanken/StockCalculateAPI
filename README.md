# 股票試算 API

<div align=center>
  <img 
    alt="Logo"
    height="150" 
    src="https://github.com/humanken/StockCalculateWeb/blob/master/public/logo.png"
  />
</div>

### 前往試算網頁：https://calculate.hotpeperken.com/web/

---
## 分支
1. master ( 開發模式，使用指令可以直接[部署](#如何部署)在Docker )

---
## 介紹
1. 根據股票10年的股利資料和收盤價計算殖利率。
2. 計算殖利率2%~8%時的股票價格，方便快速挑選心目中的股票。


### 前端
- 使用 [Vite](https://vitejs.dev/) 和 [Vue 3](https://vuejs.org/) 構建。
- 搭配 [Bootstrap 5](https://getbootstrap.com/) 
及
[Element Plus](https://element-plus.org/en-US/) 
設計具備 **響應式功能**，適應不同設備螢幕尺寸的顯示效果。
- 進行 HTTP 請求，使用 [Axios](https://axios-http.com/docs/intro) 獲取和提交資料給後端。

### 後端
- 使用 [FastAPI](https://fastapi.tiangolo.com/) 和 [Python](https://www.python.org/) 開發。
- FastAPI 是一個具有高性能優勢的 Web 框架，適合建立 APIs。
- 使用 Python 編寫各種 API 接口，並負責資料抓取和處理。
- 資料來源部分，請查看[關於資料](#關於資料)。
- 詳情，請查看[股票試算 API](#api)。

---
## 關於計算

* ### 股利資料
  計算前10年現金與股票的平均股利
  > 未滿10年股票則以目前擁有的資料計算平均

* ### 目前殖利率
  ```
  ( 現金平均股利 / 收盤價 ) * 100%
  ```
  
* ### 投資報酬率 (ROI)
  ```
  ( 淨收入 / 成本 ) * 100%
  ```
  >   以一張 (1000股) 進行計算  
  > 
  > **淨收入：**
  > ```
  > 現金平均股利 * 1000 + ( 股票平均股利 / 10 ) * 收盤價 * 1000
  > ```
  > **成本：**
  > ```
  > 收盤價 * 1000
  > ```

* ### 殖利率2%～8%，推算股票價格
  ```
  ( 現金平均股利 / 殖利率 ) * 100%
  ```

  使用TradingView程式，進行回測推論結果：
  ```diff
  - 接近 殖利率 5% 適合「 賣出 」
  + 接近 殖利率 7% 適合「 買入 」
  ```
  
## 關於更新
**_後端更新期間，網站將暫停訪問_**

* ### 股利更新
  每週一 00:00 A.M ~ 00:30 A.M.

* ### 收盤價更新
  每天 00:00 A.M ~ 00:30 A.M.

## 關於資料

* ### 股票類別
  來源來自於 [Yahoo股市 類股報價](https://tw.stock.yahoo.com/class/)

* ### 股票基本資訊
  來源來自於 Yahoo股市 各類股報價，
  [水泥類股基本資訊](https://tw.stock.yahoo.com/class-quote?sectorId=1&exchange=TAI)

* ### 股票收盤價
  上市： 來源來自於 [台灣證券交易所 API](https://openapi.twse.com.tw/)  
  上櫃： 來源來自於 [證券櫃檯買賣中心 API](https://www.tpex.org.tw/openapi/)

* ### 每年股利資料
  來源來自於 Goodinfo!台灣股市資訊網，
  [2024目前已配發的股利資料](https://goodinfo.tw/tw/StockDividendPolicyList.asp?MARKET_CAT=%E5%85%A8%E9%83%A8&INDUSTRY_CAT=%E5%85%A8%E9%83%A8&YEAR=2024)

---
## 如何部署

### 1. Clone master 分支
```shell
git clone https://github.com/humanken/StockCalculateAPI.git <direction-name>
```

### 2. 進入專案目錄
```shell
cd StockCalculateAPI
```
或是
```shell
cd <direction-name>
```

### 3. 建立 Docker 映像
```shell
docker build \
--build-arg MYSQL_NAME=<mysql-name> \
--build-arg MYSQL_USER=<mysql-user> \
--build-arg MYSQL_PASSWORD=<mysql-password> \
-t <image-name> .
```

### 4. 運行 Docker 容器
```shell
docker run -d -p 8317:8317 --name <container-name> <image-name>
``` 

> 查看 Docker 存在的容器
> ```shell 
> docker ps
> ```

---
## API

### _持續更新中．．．_
