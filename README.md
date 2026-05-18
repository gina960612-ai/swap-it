# SwapIt - 以物易物媒合平台
## 期末專題作業說明文件

---

## 一、專題摘要

**專題名稱**：SwapIt - 智能以物易物媒合平台  
**專題核心理念**：透過直覺化交友式介面 + AI 媒合演算法，解決「需求雙重巧合」問題，讓大學生的閒置物品得以有效流通，實現資源最優分配。  
**目標使用者**：大學校園內有物品交換需求的學生  
**技術語言**：Python（全棧開發）  
**開發模式**：Vibe Coding - 邊設計邊實作，以可運作成品為目標  
**預期交付**：可在網頁上運行且永久存儲數據的完整平台

---

## 二、設計動機與問題分析

### 2.1 現實問題
- **傳統二手平台的限制**  
  - 現有二手平台（蝦皮、Facebook Marketplace）以金錢交易為主，對無經濟能力但物品需求相近的人造成門檻
  - 搜尋成本高：用戶需要逐一瀏覽大量商品，效率低下
  - 「需求雙重巧合」難題：A 擁有 B 想要的物品，但 B 沒有 A 想要的物品
  
- **校園生態的機會**  
  - 大學宿舍限制，許多新生購置不必要物品；舊生離校前需處理物品
  - 社團器材重複購置、教科書年年翻新但內容類同
  - 存在強烈的「需求聚落」（如同學宿舍區、同科系課程需求相似）

### 2.2 創新解決方案
採用「交友應用式媒合」概念（類似 Tinder），搭配簡易圖論演算法：
- **直覺化交互**：用戶透過左/右滑快速篩選物品，降低決策成本
- **雙向配對驗證**：只有雙方都互相感興趣（Right swipe）才能成功配對，確保交易雙方都滿意
- **聊天協商**：配對後進入一對一聊天室，討論時間、地點、交換細節
- **社群效應**：用戶可看見曾配對用戶的評價，建立信任機制

### 2.3 預期價值
- **個人層面**：快速處理閒置品，獲得所需物品，降低購置成本
- **社會層面**：提高物品利用率，減少浪費，倡導循環經濟理念
- **帕累托改進**：交換雙方都獲得更高效用，無人因交易而損失

---

## 三、系統功能說明

### 3.1 核心功能模組

#### **1. 使用者系統**
- **註冊/登入**：使用者以學號、信箱、密碼註冊，支援登入、登出、忘記密碼
- **個人檔案**：顯示用戶名稱、頭像、所在宿舍、評分（基於成功交換次數）
- **物品清單**：用戶的物品列表，可實時查看狀態（待交換、已配對、已完成）

#### **2. 物品管理**
- **上傳物品**  
  - 物品名稱、分類（見下表）
  - 所在地區（宿舍區、圖書館、教室等）
  - 物品描述（狀態、使用時長、特殊需求）
  - 上傳圖片（單張或多張）
  - 尋求物品類型（用戶期望換到什麼類別）

- **物品分類清單**

| 分類代碼 | 分類名稱 | 示例 |
|---------|--------|------|
| FUR | 家具 | 書桌、椅子、床架 |
| APP | 家電 | 風扇、冰箱、冷氣 |
| ELE | 電子產品 | 筆電、平板、充電器 |
| GAM | 遊戲電玩 | Switch、PS5、遊戲片 |
| LIF | 生活用品 | 枕頭、被子、盆栽 |
| CLO | 服飾 | 衣服、褲子、鞋子 |
| BEA | 美妝 | 保養品、化妝品、護膚品 |
| FOO | 食品 | 零食、咖啡、茶葉 |
| BOO | 圖書文具 | 教科書、筆記本、文具 |
| TRN | 交通 | 腳踏車、滑板、機車用品 |
| SPO | 運動 | 瑜伽墊、啞鈴、羽毛球 |
| OTH | 其它 | 其他未分類物品 |

- **物品狀態管理**  
  - `active`：未配對，可被瀏覽
  - `matched`：已配對，等待交換
  - `completed`：交換完成
  - `cancelled`：交換取消

#### **3. 交友式媒合機制**
- **卡片瀏覽界面**  
  - 顯示其他用戶的物品卡片（圖片、名稱、描述、所在位置）
  - 支援左滑（不感興趣）、右滑（感興趣）、上滑（標記為稍後決定）
  
- **配對邏輯**  
  - 若 User A 右滑 User B 的物品 I，系統記錄 A 的興趣
  - 當 User B 右滑 User A 的物品 J 時，系統檢測「互相感興趣」，觸發配對成功
  - 配對成功後，自動開啟聊天室
  
- **推薦演算法（簡易版）**  
  - 基於物品分類相似度、用戶地理位置近距離、用戶興趣標籤匹配
  - 優先推薦高評分用戶的物品

#### **4. 配對後聊天系統**
- **一對一聊天室**  
  - 配對雙方可進入獨立聊天室
  - 支援文字訊息、時間戳記、已讀狀態

- **聊天內容**  
  - 討論交換物品的具體細節（交換時間、地點、額外條件）
  - 支援確認交換完成 → 自動更新物品狀態為 `completed`
  - 支援回報交換失敗或取消交換

- **評價系統**  
  - 交換完成後，雙方可為對方評分（1-5星）和留評論
  - 評分用於推薦演算法與信任機制

#### **5. 圖形化介面（Web 前端）**
- **首頁/儀表板**  
  - 顯示用戶的未讀訊息、待配對物品、成功交換統計
  
- **物品卡片瀏覽**  
  - 類 Tinder 介面，支援拖拽或按鈕左/右滑
  - 顯示物品詳細資訊（可展開查看）
  
- **聊天列表**  
  - 顯示所有進行中或已完成的配對聊天
  
- **個人中心**  
  - 編輯個人檔案、查看歷史交換、管理已上傳物品

### 3.2 使用流程示意

```
1. 新使用者進入系統
   ↓
2. 註冊/登入帳號
   ↓
3. 完善個人檔案 + 上傳待交換物品
   ↓
4. 瀏覽其他用戶物品卡片（左/右滑）
   ↓
5. 系統偵測配對（雙向 Right swipe）
   ↓
6. 進入聊天室協商交換細節
   ↓
7. 雙方確認交換完成
   ↓
8. 系統記錄交換紀錄、互相評分
   ↓
9. 物品狀態更新、用戶信譽度提升
```

---

## 四、系統架構與技術設計

### 4.1 技術栈選擇

| 層級 | 技術選擇 | 理由 |
|-----|---------|------|
| **全棧框架** | Python Streamlit | 純 Python 開發前後端，無需 HTML/CSS/JS，快速成型 |
| **後端邏輯** | Python OOP + 自訂模組 | 核心業務邏輯用 OOP 設計，推薦演算法、配對邏輯等 |
| **數據庫** | SQLite + SQLAlchemy ORM | ORM 方式操作數據庫，所有代碼都是 Python |
| **部署** | Streamlit Cloud / Heroku | 無需獨立部署，Streamlit Cloud 直接部署 Python 代碼 |

**為什麼選擇 Streamlit？**
- ✅ 零前端代碼：所有 UI 用 Python 描述（`st.card()`, `st.button()` 等）
- ✅ 快速開發：聚焦業務邏輯，不浪費時間在 HTML/CSS
- ✅ 實時交互：自動偵測數據變化，重新執行 Python 代碼
- ✅ 輕鬆部署：Streamlit Cloud 一鍵部署，無需服務器配置
- ✅ 適合教學：大一下課程用 Python 實現完整項目

### 4.2 數據庫模型設計（SQLAlchemy ORM）

在 Streamlit 中，所有數據庫操作都用 Python 代碼完成，無需寫 SQL。以下是核心模型定義：

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from datetime import datetime

Base = declarative_base()

# 表 1：用戶模型
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt 加密
    dorm = Column(String(50))
    avatar_url = Column(String(255))
    rating = Column(Float, default=0.0, index=True)  # 信譽評分
    completed_trades = Column(Integer, default=0)
    bio = Column(String(500))
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯
    items = relationship("Item", back_populates="owner")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id")

# 表 2：物品模型
class Item(Base):
    __tablename__ = 'items'
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(10), nullable=False, index=True)  # FUR, APP, ELE, GAM, etc.
    description = Column(Text)
    location = Column(String(100))
    image_url = Column(String(255))
    seeking_categories = Column(String(100))  # 期望類別，逗號分隔
    status = Column(String(20), default='active', index=True)  # active, matched, completed, cancelled
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 關聯
    owner = relationship("User", back_populates="items")

# 表 3：滑動記錄模型
class Swipe(Base):
    __tablename__ = 'swipes'
    
    swipe_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete='CASCADE'), nullable=False)
    direction = Column(String(10), nullable=False)  # 'right', 'left', 'skip'
    created_at = Column(DateTime, default=datetime.now)

# 表 4：配對模型
class Match(Base):
    __tablename__ = 'matches'
    
    match_id = Column(Integer, primary_key=True, autoincrement=True)
    user_a_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    item_a_id = Column(Integer, ForeignKey('items.item_id', ondelete='CASCADE'), nullable=False)
    item_b_id = Column(Integer, ForeignKey('items.item_id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), default='active', index=True)  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 表 5：聊天室模型
class ChatRoom(Base):
    __tablename__ = 'chat_rooms'
    
    chat_room_id = Column(Integer, primary_key=True, autoincrement=True)
    user_a_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey('matches.match_id', ondelete='CASCADE'), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)
    
    messages = relationship("Message", back_populates="chat_room")

# 表 6：訊息模型
class Message(Base):
    __tablename__ = 'messages'
    
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_room_id = Column(Integer, ForeignKey('chat_rooms.chat_room_id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    chat_room = relationship("ChatRoom", back_populates="messages")

# 表 7：評價模型
class Review(Base):
    __tablename__ = 'reviews'
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.match_id', ondelete='CASCADE'), nullable=False, unique=True)
    reviewer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    reviewee_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 星
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# 初始化數據庫
def init_db(database_url="sqlite:///swapit.db"):
    """初始化數據庫連接與表結構"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine

## 部署到 Streamlit Cloud

如果你想要把 SwapIt 直接部署到網路上，請參考 `DEPLOYMENT_GUIDE.md`。

基本流程：
1. 把專案推到 GitHub。
2. 登入 Streamlit Cloud（https://share.streamlit.io）。
3. 建立新應用，主程式檔案設定為 `app.py`。
4. 若要使用 PostgreSQL，請在 Streamlit Cloud 的 Secrets 中設定 `DATABASE_URL`。

專業部署說明請參考：`DEPLOYMENT_GUIDE.md`
```

**使用 SQLAlchemy 的優勢**：
- ✅ 純 Python 代碼，無需手寫 SQL
- ✅ 自動建立表、索引、外鍵關係
- ✅ 數據驗證與關聯管理
- ✅ 支援多種數據庫（SQLite / PostgreSQL / MySQL）

### 4.3 核心類別設計（虛擬程式碼）

#### **用戶類別 (User)**
```python
class User:
    def __init__(self, user_id, name, email, password, dorm):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = hash(password)  # 加密存儲
        self.dorm = dorm  # 所在宿舍
        self.items = []  # 用戶的物品列表 [Item]
        self.rating = 0.0  # 交換信譽評分
        self.completed_trades = 0  # 成功交換次數
    
    def add_item(self, item):
        """上傳新物品"""
        item.owner_id = self.user_id
        self.items.append(item)
        return item
    
    def get_active_items(self):
        """取得待交換物品"""
        return [item for item in self.items if item.status == 'active']
    
    def update_rating(self, score, review):
        """更新用戶評分"""
        self.rating = (self.rating * self.completed_trades + score) / (self.completed_trades + 1)
        self.completed_trades += 1
```

#### **物品類別 (Item)**
```python
class Item:
    def __init__(self, item_id, name, category, description, location, image_url):
        self.item_id = item_id
        self.owner_id = None  # 由 User 設置
        self.name = name
        self.category = category  # e.g., 'book', 'furniture', 'clothes'
        self.description = description
        self.location = location  # 所在位置
        self.image_url = image_url
        self.status = 'active'  # active, matched, completed, cancelled
        self.seeking_categories = []  # 期望換到的物品分類
        self.created_at = datetime.now()
    
    def update_status(self, new_status):
        """更新物品狀態"""
        valid_statuses = ['active', 'matched', 'completed', 'cancelled']
        if new_status in valid_statuses:
            self.status = new_status
        else:
            raise ValueError(f"Invalid status: {new_status}")
    
    def to_dict(self):
        """轉換為字典格式（用於 UI 顯示與序列化）"""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'image_url': self.image_url,
            'status': self.status
        }
```

#### **配對類別 (Match)**
```python
class Match:
    def __init__(self, match_id, user_a, user_b, item_a, item_b):
        self.match_id = match_id
        self.user_a_id = user_a.user_id
        self.user_b_id = user_b.user_id
        self.item_a_id = item_a.item_id  # User A 提供
        self.item_b_id = item_b.item_id  # User B 提供
        self.status = 'active'  # active, completed, cancelled
        self.created_at = datetime.now()
        self.completed_at = None
    
    def complete_trade(self):
        """標記交換完成"""
        self.status = 'completed'
        self.completed_at = datetime.now()
        # 更新物品狀態
        # item_a.update_status('completed')
        # item_b.update_status('completed')
    
    def get_chat_room_id(self):
        """取得聊天室 ID"""
        return f"chat_{min(self.user_a_id, self.user_b_id)}_{max(self.user_a_id, self.user_b_id)}"
```

#### **聊天室類別 (ChatRoom)**
```python
class ChatRoom:
    def __init__(self, chat_room_id, user_a_id, user_b_id, match_id):
        self.chat_room_id = chat_room_id
        self.user_a_id = user_a_id
        self.user_b_id = user_b_id
        self.match_id = match_id
        self.messages = []  # [Message]
        self.created_at = datetime.now()
    
    def send_message(self, sender_id, content):
        """發送訊息"""
        message = Message(
            sender_id=sender_id,
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(message)
        return message
    
    def get_message_history(self, limit=50):
        """取得訊息歷史"""
        return self.messages[-limit:]

class Message:
    def __init__(self, sender_id, content, timestamp):
        self.sender_id = sender_id
        self.content = content
        self.timestamp = timestamp
        self.read = False
    
    def mark_as_read(self):
        self.read = True
```

#### **推薦引擎類別 (RecommendationEngine)**
```python
class RecommendationEngine:
    def __init__(self, all_users):
        self.all_users = all_users
    
    def get_recommendations(self, user_id, limit=10):
        """為指定用戶推薦物品"""
        current_user = next(u for u in self.all_users if u.user_id == user_id)
        candidates = []
        
        for other_user in self.all_users:
            if other_user.user_id == user_id:
                continue
            
            for item in other_user.get_active_items():
                # 計算相似度：分類匹配 + 距離近 + 高評分
                similarity_score = self._calculate_similarity(current_user, item, other_user)
                candidates.append((item, similarity_score))
        
        # 排序並返回前 limit 個
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in candidates[:limit]]
    
    def _calculate_similarity(self, user, item, item_owner):
        """計算相似度分數"""
        score = 0.0
        
        # 分類相似度（用戶尋求的類別 vs 物品分類）
        if item.category in user.items[0].seeking_categories if user.items else []:
            score += 3.0
        
        # 距離相似度（同區域加分）
        if user.dorm == item_owner.dorm:
            score += 2.0
        
        # 信譽度（高評分用戶優先）
        score += item_owner.rating
        
        return score
```

### 4.4 聊天系統實現方案（Streamlit）

**Streamlit 中的聊天實現**：

Streamlit 提供內建聊天組件 `st.chat_message()` 和 `st.chat_input()`，無需輪詢，自動重新執行代碼。

```python
import streamlit as st
from sqlalchemy.orm import Session
from datetime import datetime

def display_chat_room(db: Session, match_id: int, current_user_id: int):
    """顯示聊天室並處理訊息"""
    
    # 從數據庫取得聊天室
    chat_room = db.query(ChatRoom).filter(ChatRoom.match_id == match_id).first()
    if not chat_room:
        st.error("聊天室不存在")
        return
    
    # 顯示訊息歷史
    st.subheader("聊天")
    messages = db.query(Message).filter(
        Message.chat_room_id == chat_room.chat_room_id
    ).order_by(Message.created_at).all()
    
    for msg in messages:
        sender = db.query(User).get(msg.sender_id)
        with st.chat_message(sender.name):
            st.write(msg.content)
            st.caption(msg.created_at.strftime("%Y-%m-%d %H:%M"))
    
    # 输入欄：用戶發送訊息
    user_input = st.chat_input("輸入訊息...")
    
    if user_input:
        # 保存訊息到數據庫
        new_message = Message(
            chat_room_id=chat_room.chat_room_id,
            sender_id=current_user_id,
            content=user_input,
            created_at=datetime.now()
        )
        db.add(new_message)
        db.commit()
        
        # Streamlit 自動重新執行，訊息立即顯示
        st.rerun()
    
    # 確認交換完成按鈕
    if st.button("✅ 確認交換完成"):
        match = db.query(Match).get(match_id)
        match.status = 'completed'
        match.completed_at = datetime.now()
        db.commit()
        st.success("交換已標記為完成！")
        st.rerun()
```

**Streamlit 聊天的優勢**：
- ✅ 無需 WebSocket 或輪詢，自動重新執行代碼
- ✅ 內建聊天氣泡樣式，無需手寫 CSS
- ✅ `st.rerun()` 自動刷新頁面
- ✅ 純 Python 實現，無 JavaScript 代碼



### 4.5 系統架構圖（文字描述）

```
┌──────────────────────────────────────────────────────────┐
│         Web 應用 (Streamlit 前後端一體化)                │
│  - 使用者介面 (卡片瀏覽、聊天、個人檔案)                 │
│  - 全 Python 邏輯 (OOP 類別、推薦引擎)                   │
│  - 自動交互更新 (st.rerun() 重新執行代碼)               │
└────────────────┬─────────────────────────────────────────┘
                 │ Python 代碼執行
┌────────────────▼─────────────────────────────────────────┐
│              業務邏輯層 (Python OOP)                       │
│  - User、Item、Match、ChatRoom 類別                      │
│  - 配對演算法、推薦引擎                                  │
│  - 用戶認證、數據驗證                                    │
└────────────────┬─────────────────────────────────────────┘
                 │ SQLAlchemy ORM
┌────────────────▼─────────────────────────────────────────┐
│          數據層 (SQLite + SQLAlchemy)                     │
│  - users (用戶表)       - items (物品表)                │
│  - swipes (滑動記錄)    - matches (配對表)              │
│  - chat_rooms (聊天室)  - messages (訊息表)             │
│  - reviews (評價表)                                     │
└──────────────────────────────────────────────────────────┘
```

**Streamlit 的工作流程**：
1. 用戶在 Web 頁面操作（點擊、輸入）
2. Streamlit 自動偵測交互事件
3. Python 代碼從上到下重新執行
4. SQLAlchemy 更新數據庫
5. UI 自動刷新，顯示最新結果
6. 無需 REST API 或 JavaScript，所有邏輯都在 Python 中

### 4.6 核心業務邏輯函數（Python）

由於 Streamlit 不需要 REST API，所有操作都是 Python 函數調用。以下是核心函數界面：

```python
# ===== 用戶管理 =====
def register_user(db: Session, email: str, password: str, name: str, dorm: str) -> User:
    """用戶註冊"""
    
def login_user(db: Session, email: str, password: str) -> Optional[User]:
    """用戶登入驗證"""

def update_user_profile(db: Session, user_id: int, name: str, bio: str, dorm: str) -> User:
    """更新用戶檔案"""

# ===== 物品管理 =====
def add_item(db: Session, owner_id: int, name: str, category: str, description: str, 
             location: str, seeking_categories: str) -> Item:
    """用戶上傳新物品"""

def get_user_items(db: Session, user_id: int) -> List[Item]:
    """取得用戶的物品清單"""

def get_active_items(db: Session, user_id: int) -> List[Item]:
    """取得待交換物品（狀態 = 'active'）"""

# ===== 推薦引擎 =====
def get_recommendations(db: Session, user_id: int, limit: int = 10) -> List[Item]:
    """為用戶推薦物品（基於分類匹配、地理位置、信譽度）"""
    # 分類相似度：權重 3.0
    # 地理位置相似度：權重 2.0
    # 所有者信譽度：權重 1.0

# ===== 滑動與配對 =====
def record_swipe(db: Session, user_id: int, item_id: int, direction: str) -> Optional[Match]:
    """
    記錄用戶的滑動動作
    direction: 'right'（喜歡）、'left'（不喜歡）、'skip'（稍後）
    若已存在雙向配對，自動建立 Match 對象
    """

def get_matches(db: Session, user_id: int) -> List[Match]:
    """取得用戶的所有配對"""

def complete_trade(db: Session, match_id: int) -> Match:
    """標記交換完成"""

# ===== 聊天系統 =====
def send_message(db: Session, chat_room_id: int, sender_id: int, content: str) -> Message:
    """發送聊天訊息"""

def get_message_history(db: Session, chat_room_id: int, limit: int = 50) -> List[Message]:
    """取得聊天歷史（最近 50 條）"""

# ===== 評價系統 =====
def add_review(db: Session, match_id: int, reviewer_id: int, reviewee_id: int, 
               rating: int, comment: str) -> Review:
    """提交交換評價"""

def update_user_rating(db: Session, user_id: int) -> float:
    """根據所有評價計算用戶的平均信譽評分"""
```

**Streamlit 中的調用示例**：
```python
import streamlit as st
from sqlalchemy.orm import Session

# 在 Streamlit 應用中調用
if st.button("上傳物品"):
    new_item = add_item(
        db=db,
        owner_id=st.session_state.user_id,
        name=st.text_input("物品名稱"),
        category=st.selectbox("分類", ["FUR", "APP", "ELE", "GAM", "LIF", "CLO", "BEA", "FOO", "BOO", "TRN", "SPO", "OTH"]),
        description=st.text_area("描述"),
        location=st.text_input("位置"),
        seeking_categories=st.multiselect("期望換到的分類", CATEGORIES)
    )
    st.success("物品已上傳！")

# 推薦物品列表
recommendations = get_recommendations(db, st.session_state.user_id, limit=10)
for item in recommendations:
    st.write(f"**{item.name}** - {item.category}")
```

### 4.7 安全與隱私設計

#### 4.7.1 密碼安全
```python
from werkzeug.security import generate_password_hash, check_password_hash

# 用戶註冊時：使用 bcrypt 加密密碼
password_hash = generate_password_hash(user_input_password, method='bcrypt')

# 用戶登入時：驗證密碼
is_correct = check_password_hash(stored_hash, user_input_password)
```

**密碼政策**：
- 最小 8 字元，包含大小寫與數字
- 密碼以 bcrypt 加鹽存儲，不可逆
- 禁止明文傳輸，所有網路通訊使用 HTTPS

#### 4.7.2 郵箱驗證
```python
# 用戶註冊時產生驗證 token
verification_token = secrets.token_urlsafe(32)  # 安全隨機 token

# 發送驗證郵件
send_email(user_email, f"https://swapit.com/verify/{verification_token}")

# 用戶點擊郵件連結後，驗證 token 並更新 email_verified = True
```

#### 4.7.3 身份驗證
- **會話管理**：使用 Streamlit 的 `st.session_state` 存儲用戶 ID
- **Token 驗證**：後端可使用 JWT token，存儲在 session state 中
- **登入檢查**：Streamlit 應用啟動時檢查用戶是否已登入

#### 4.7.4 個人資料隱私保護
| 隱私項目 | 保護措施 |
|---------|---------|
| **聯絡方式** | 僅限配對方可見，不向其他用戶展示 |
| **宿舍位置** | 精確到宿舍區（如「宿舍 A 區」），不顯示具體房號 |
| **交換歷史** | 只有自己與交換對象可查看，其他用戶不可見 |
| **聊天訊息** | 只有參與聊天的兩方可讀，伺服器日誌不記錄訊息內容 |
| **IP 位址** | 不記錄用戶 IP 地址 |

#### 4.7.5 數據安全措施
- **SQL Injection 防護**：使用參數化查詢 (ORM)，不直接拼接 SQL
- **XSS 防護**：前端對用戶輸入進行 HTML escape
- **CSRF 防護**：所有 POST/PUT/DELETE 請求驗證 CSRF token
- **API Rate Limiting**：防止暴力攻擊（如登入嘗試超過 5 次/分鐘則鎖定）



---

## 五、專題與評分標準對應

### 評分標準 1️⃣：設計概念（20%）

| 評分項目 | SwapIt 的優勢 |
|---------|--------------|
| **創意性** | 結合「以物易物」+ 「交友式媒合」，打破傳統二手平台單向搜尋模式，創新度高 |
| **獨特性** | 專注校園場景，充分利用高密度需求聚落，差異於通用二手平台 |
| **問題認知** | 明確指出「需求雙重巧合」與「搜尋成本」等現實問題，而非空洞概念 |
| **解決方案** | 提供具體的技術方案（雙向配對、聊天協商、評分機制），邏輯自洽 |
| **社會價值** | 倡導循環經濟與資源最優分配，具社會意義 |

### 評分標準 2️⃣：作品完整度（30%）

| 功能模組 | 完整性 | 說明 |
|---------|-------|------|
| **使用者系統** | 100% | 完整的註冊、登入、檔案管理流程 |
| **物品管理** | 100% | 上傳、編輯、刪除、狀態追蹤完整 |
| **媒合機制** | 100% | 卡片瀏覽、左右滑、雙向配對邏輯完備 |
| **聊天系統** | 100% | 配對後聊天、訊息記錄、交換確認 |
| **評價系統** | 100% | 交換後評分、信譽積累機制 |
| **前端介面** | 100% | Web UI 支援所有核心功能 |
| **數據持久化** | 100% | 數據永久存儲於數據庫 |
| **部署上線** | 100% | 可部署至雲端平台供他人使用 |

**完整度結論**：每個使用者從「進入系統」到「完成交換」的全流程皆有覆蓋，無功能缺口。

### 評分標準 3️⃣：作品可落實性（30%）

#### 3.1 實際問題解決
- **問題 A：物品需求難以匹配**  
  → **解決方案**：推薦演算法基於分類、地理位置、用戶信譽，提高配對成功率
  
- **問題 B：決策成本高**  
  → **解決方案**：交友式卡片介面 (左/右滑)，2 秒內完成一個決策
  
- **問題 C：交易信任度低**  
  → **解決方案**：評分機制 + 聊天記錄 + 交換歷史，建立信譽體系

#### 3.2 校園應用場景
1. **新生入學**：舊宿舍物品 ↔ 新宿舍需求，快速流轉
2. **季節交換**：冬衣 ↔ 夏衣、課本年度更新
3. **社團器材**：重複購置 → 共享借用
4. **畢業清空**：四年級物品分散至低年級學生

#### 3.3 用戶規模與擴展
- **初期目標**：單一校園 1000~5000 活躍用戶
- **中期擴展**：多校園聯動、跨校園交換
- **長期願景**：城市級別以物易物網絡

#### 3.4 技術可行性
- ✅ **業務邏輯**：基於 OOP 設計，核心演算法複雜度低 O(n log n)
- ✅ **前端交互**：Streamlit 內建組件（st.selectbox、st.button、st.chat_message），無需手寫 HTML/CSS/JS
- ✅ **數據存儲**：SQLite 支援本地開發，PostgreSQL 支援雲端部署
- ✅ **部署成本**：Streamlit Cloud 免費方案，無需伺服器配置
- ✅ **2-3 人團隊**：Streamlit 開發 1-2 人、業務邏輯 & 算法 1 人，分工簡化明確

### 評分標準 4️⃣：技術深度（20%）

#### 5.4.1 物件導向程式設計 (OOP) 的應用

| OOP 原則 | SwapIt 的實現 |
|---------|--------------|
| **封裝 (Encapsulation)** | User、Item、Match、ChatRoom 各自管理私有屬性與方法；隱藏內部實現 |
| **繼承 (Inheritance)** | 可設計 Entity 基類，User/Item 繼承共同屬性（created_at、updated_at）；Streamlit 應用可繼承基礎頁面類 |
| **多態 (Polymorphism)** | 不同物品類型（书、衣物、电子产品）有統一介面但不同行為（e.g., 書籍可展示 ISBN，衣物可展示尺寸） |
| **抽象 (Abstraction)** | RecommendationEngine 抽象推薦邏輯；DatabaseManager 抽象 SQLAlchemy 操作 |

#### 5.4.2 設計模式應用
- **Strategy Pattern**：推薦演算法可切換（基於分類、基於信譽、基於距離）
- **Observer Pattern**：當配對成功時通知雙方用戶
- **Repository Pattern**：數據存取層統一管理 CRUD 操作（SQLAlchemy）
- **Factory Pattern**：Streamlit 組件工廠，統一創建 UI 元素

#### 5.4.3 演算法與資料結構
- **圖論應用**：用戶 - 物品配對圖，配對即尋找二部圖匹配
- **推薦演算法**：加權評分 (Weighted Scoring)，基於分類相似度、地理距離、信譽度
- **數據結構**：SQLAlchemy 關聯優化、索引加速查詢、排序演算法優化推薦結果

#### 5.4.4 Streamlit 全棧集成
- **單一代碼庫**：前後端同語言（Python），無需 REST API 橋接
- **交互式更新**：`st.rerun()` 自動重新執行，實現即時反應
- **會話管理**：`st.session_state` 管理用戶狀態，跨多頁應用持久化
- **數據綁定**：Streamlit 組件直接調用 Python 業務函數，無中間層

#### 5.4.5 數據庫設計
- **規範化設計 (Database Normalization)**：避免數據冗餘，確保一致性
- **索引優化**：user_id、item_id、match_id 等字段建立索引，加快查詢
- **SQLAlchemy ORM**：自動處理關聯關係，支援複雜查詢優化
- **交易一致性**：配對與聊天室的原子性操作

#### 5.4.6 技術難度總結

| 難度區間 | 評估 |
|---------|------|
| **低** | 簡單 CRUD 操作、基本 Streamlit UI |
| **中** | ✓ **推薦演算法、雙向配對邏輯、聊天系統實時更新、OOP 架構設計** |
| **高** | 大規模併發處理、分佈式推薦系統、機器學習模型集成

---

## 六、自創程度說明

### 6.1 參考與創新的平衡

| 構成要素 | 來源與自創程度 |
|---------|--------------|
| **交友式滑動介面** | 參考 Tinder / Bumble 的卡片滑動設計；自行設計應用於二手交換場景 |
| **推薦演算法** | 參考通用推薦系統概念（協同過濾、內容過濾）；自行簡化為加權評分，針對校園場景優化 |
| **雙向配對邏輯** | 自創，非現有二手平台的標準做法，體現專案創新點 |
| **OOP 架構** | 標準 Python 面向物件設計；應用於該項目的業務邏輯為自創 |
| **聊天系統** | 基於 Streamlit 內建組件（st.chat_message）；集成至本項目為自創應用 |

### 6.2 「自創」vs「整合」的界定

✅ **自創部分**：
- 從問題分析到解決方案的完整設計過程
- 雙向配對邏輯與推薦演算法的具體實現
- 系統架構的整體規劃與 Python OOP 類別設計
- Streamlit 頁面設計與業務邏輯集成
- 代碼實現與調試

❌ **參考部分**（合理使用開源資源）：
- Streamlit 框架（Web 框架，產業標準）
- SQLAlchemy ORM（數據庫抽象層，產業標準）
- Werkzeug（密碼加密庫）
- Python 標準庫（datetime、secrets 等）

### 6.3 代碼原創性承諾

- 核心業務邏輯類別（User、Item、Match 等）**100% 自行撰寫**
- API 路由與邏輯**自行實現**，不直接複製第三方範本
- 前端交互與界面**自行設計與調整**
- 所有代碼提交至 GitHub，保留完整開發歷史

---

## 七、實現時程與分工建議

### 7.1 開發階段（2-4 週）

| 周次 | Streamlit 應用開發 | 業務邏輯 & 算法 | 測試 & 部署 |
|-----|---------|---------|-----------|
| **第 1 周** | - 項目架構搭建<br>- User & Item 模型設計<br>- 登入/註冊頁面 | - 數據庫初始化 (SQLAlchemy)<br>- 推薦演算法原型<br>- 用戶認證函數 | - pytest 測試框架<br>- 本地測試環境 |
| **第 2 周** | - 卡片瀏覽頁 (Streamlit)<br>- 物品上傳頁面<br>- 個人檔案頁面 | - Match 配對邏輯<br>- 推薦引擎完整實現<br>- 評價系統 | - 單元測試 (test_models.py)<br>- 數據導入腳本 |
| **第 3 周** | - 聊天室頁 (st.chat_message)<br>- Streamlit 多頁應用設定<br>- 會話狀態管理 | - 聊天功能 Python 實現<br>- ChatRoom 類別完成<br>- 性能優化 | - 集成測試<br>- 邊界情況測試 |
| **第 4 周** | - UI 細節調整<br>- Streamlit 主題配置<br>- 本地功能驗收 | - 完整性測試<br>- 代碼審查 | - 部署至 Streamlit Cloud<br>- 線上測試<br>- 文檔撰寫 |

### 7.2 人員分工

由於使用 Streamlit（純 Python 前後端一體化），分工簡化為：

- **Streamlit 應用開發者**（1-2 人）：
  - 負責 Streamlit 頁面與交互邏輯
  - 調用業務邏輯函數，將結果展示在 UI
  - 負責會話管理、數據輸入驗證

- **業務邏輯 & 算法工程師**（1 人）：
  - 負責 SQLAlchemy ORM 模型設計
  - 實現核心邏輯：配對、推薦、評價系統
  - 性能優化與索引設計

- **測試 & 部署**（可由以上人員兼任）：
  - 單元測試 (pytest)
  - 集成測試與 UAT
  - Streamlit Cloud 部署

### 7.3 測試計畫
- **單元測試**：測試各類別的方法 (pytest)
- **集成測試**：測試 API 端對端流程
- **用戶驗收測試 (UAT)**：邀請 5~10 名學生試用，收集反饋

---

## 八、技術棧與部署方案

### 8.1 本地開發環境

```
Python 3.9+
├── Streamlit              (Web 框架 - 前後端一體化)
├── SQLAlchemy + SQLite    (ORM + 數據庫)
├── Werkzeug               (密碼加密)
├── python-dotenv          (環境變數管理)
└── pytest                 (單元測試)
```

**安裝依賴**：
```bash
pip install streamlit sqlalchemy werkzeug python-dotenv pytest pillow
```

**本地執行**：
```bash
streamlit run app.py
```

### 8.2 Streamlit 部署方案

**推薦部署至 Streamlit Cloud**（最簡單）：

```
GitHub 上傳代碼
    ↓
Streamlit Cloud 自動檢測 streamlit run
    ↓
自動部署 Python 應用
    ↓
https://app-name.streamlit.app （公開 URL）
```

**優勢**：
- ✅ 零服務器配置，一鍵部署
- ✅ 自動扩展，支援數千併發用戶
- ✅ 免費方案足以支撐校園規模
- ✅ 自動 HTTPS、域名管理

**替代方案**：Heroku / Railway（需付費）

### 8.3 項目文件結構

```
swapit/
├── app.py                          # Streamlit 主應用
├── models.py                       # SQLAlchemy 模型定義
├── utils.py                        # 工具函數（推薦、配對等）
├── database.py                     # 數據庫初始化與連接
├── pages/
│   ├── 1_Browse.py                # 卡片瀏覽頁
│   ├── 2_Chat.py                  # 聊天頁
│   ├── 3_MyItems.py               # 我的物品
│   └── 4_Profile.py               # 個人檔案
├── tests/
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_auth.py
├── requirements.txt                # Python 依賴
├── .streamlit/
│   └── config.toml                # Streamlit 配置
├── swapit.db                      # SQLite 數據庫（本地）
└── README.md                      # 項目說明
```

### 8.4 Streamlit 應用結構（核心代碼）

**app.py（主入口）**：
```python
import streamlit as st
from database import init_db, get_session
from models import User

st.set_page_config(page_title="SwapIt", layout="wide")

# 初始化會話
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

db = get_session()

# 主頁邏輯
if st.session_state.user_id is None:
    # 顯示登入/註冊
    st.title("SwapIt - 以物易物媒合平台")
    tab1, tab2 = st.tabs(["登入", "註冊"])
    
    with tab1:
        email = st.text_input("電子郵件")
        password = st.text_input("密碼", type="password")
        if st.button("登入"):
            user = login_user(db, email, password)
            if user:
                st.session_state.user_id = user.user_id
                st.success("登入成功！")
                st.rerun()
            else:
                st.error("登入失敗")
    
    with tab2:
        # 註冊邏輯
        pass
else:
    # 已登入 - 顯示側邊欄導航
    st.sidebar.title("菜單")
    page = st.sidebar.radio("選擇", ["卡片瀏覽", "我的物品", "聊天", "檔案"])
    
    if st.sidebar.button("登出"):
        st.session_state.user_id = None
        st.rerun()
    
    # 根據選擇顯示不同頁面
    if page == "卡片瀏覽":
        st.title("發現物品")
        # 推薦邏輯...
```

### 8.5 環境配置文件

**requirements.txt**：
```
streamlit==1.28.0
sqlalchemy==2.0.20
werkzeug==2.3.7
python-dotenv==1.0.0
pytest==7.4.0
pillow==10.0.0
```

**.streamlit/config.toml**：
```toml
[theme]
primaryColor = "#FF6B9D"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
headless = true
```

---

## 九、預期成果與驗收標準

### 9.1 功能驗收

- ✓ 用戶可完整註冊、登入、建立檔案
- ✓ 可上傳 ≥ 5 項物品，每項可包含圖片
- ✓ 卡片瀏覽界面流暢，支援左/右滑
- ✓ 配對成功後自動開啟聊天室
- ✓ 聊天訊息實時顯示 (或 ≤ 1 秒延遲)
- ✓ 完成交換後可評分，評分正確累積至用戶信譽
- ✓ 數據持久化，重啟應用不丟失數據

### 9.2 性能指標

| 指標 | 目標 | 說明 |
|-----|------|------|
| **頁面交互響應** | ≤ 1s | 用戶點擊卡片後立即反應（Streamlit 重新執行代碼） |
| **頁面加載時間** | ≤ 3s | Streamlit Cloud 首次加載應用 |
| **數據庫查詢** | ≤ 100ms | 推薦引擎查詢使用索引加速 |
| **併發用戶支持** | ≥ 100+ 同時在線用戶 | Streamlit Cloud 自動水平擴展 |
| **聊天訊息延遲** | ≤ 1s | 用戶輸入到顯示的延遲 |

### 9.3 部署驗收

- ✓ 可在公開 Streamlit Cloud URL 訪問 (如 https://swapit.streamlit.app)
- ✓ 新用戶可直接使用，無需本地配置或安裝
- ✓ 數據在 SQLite 數據庫永久存儲
- ✓ 多用戶併發訪問穩定運行

---

## 十、結論與未來擴充方向

### 10.1 專題總結

SwapIt 以物易物媒合平台通過**創新的交友式介面**與**智能推薦演算法**，有效解決校園物品流通的痛點問題。專案具有：

1. **設計創意**：融合多領域概念，打造獨特的市場定位
2. **技術完整**：從 OOP 架構到全 Python Streamlit 應用，體現完整的軟體工程能力
3. **社會價值**：倡導循環經濟，減少浪費，資源高效利用
4. **落實可能**：技術棧成熟、團隊分工明確、部署方案簡單（Streamlit Cloud 一鍵部署）
5. **大一下適配**：純 Python 實現，符合本學期課程內容

### 10.2 未來擴充方向

#### **短期（3-6 個月）**
- 🔸 實時聊天通知 (WebSocket / Push Notification)
- 🔸 進階推薦演算法 (協同過濾、機器學習)
- 🔸 移動應用版本 (React Native / Flutter)
- 🔸 交換完成後自動提醒線下交易

#### **中期（6-12 個月）**
- 🔶 多校園聯動系統
- 🔶 積分兌換機制 (對沖邊界用戶)
- 🔶 社團/組織級物品共享
- 🔶 AI 虛擬小助手（FAQ、配對提示）

#### **長期（1-2 年）**
- 🔴 城市級以物易物網絡
- 🔴 物品評估與價值定級系統
- 🔴 供應鏈整合 (與捐贈機構、回收企業合作)
- 🔴 區塊鏈信譽系統 (跨平台可移轉信譽)

### 10.3 最終期許

期望 SwapIt 不僅作為大學資工導論的課程專題，更能成為一個**實際可用的校園公共服務**，讓資源高效流動，讓學生以零成本獲取所需，踐行循環經濟理想。

---

## 十一、參考資料與附錄

### 相關技術文件
- Streamlit 官方文檔：https://docs.streamlit.io/
- SQLAlchemy ORM：https://docs.sqlalchemy.org/
- Python 密碼安全 (Werkzeug)：https://werkzeug.palletsprojects.com/security/
- OOP 設計模式：https://en.wikipedia.org/wiki/Design_pattern_(computer_science)
- 推薦系統基礎：https://en.wikipedia.org/wiki/Collaborative_filtering

### 開發工具
- VS Code / PyCharm (IDE)
- Git / GitHub (版本控制)
- Streamlit Cloud (部署平台)
- Python 3.9+ (語言環境)

### 部署平台
- Streamlit Cloud：https://streamlit.io/cloud （推薦，免費且簡單）
- Heroku：https://www.heroku.com/ （需付費，但支援 Python）
- Railway：https://railway.app/ （免費層有額度）

### 課程相關
- 本專題使用 Python 實現，符合「大一下資工導論」課程要求
- 強調 OOP、數據結構、數據庫操作等核心概念

---

**文件編制日期**：2026 年 5 月 15 日  
**專題團隊**：[請填入團隊成員名單]  
**指導教授**：[請填入教授名字]
