from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


CATEGORIES = {
    "FUR": "家具",
    "APP": "家電",
    "ELE": "電子產品",
    "GAM": "遊戲",
    "LIF": "生活用品",
    "CLO": "服飾",
    "BEA": "美妝保養",
    "FOO": "食品",
    "BOO": "書籍",
    "TRN": "交通用品",
    "SPO": "運動用品",
    "OTH": "其他",
}

TAIWAN_LOCATIONS = {
    "臺北市": (25.0375, 121.5637),
    "新北市": (25.0120, 121.4657),
    "桃園市": (24.9937, 121.3009),
    "臺中市": (24.1618, 120.6469),
    "臺南市": (22.9999, 120.2269),
    "高雄市": (22.6273, 120.3014),
    "基隆市": (25.1276, 121.7392),
    "新竹市": (24.8138, 120.9675),
    "嘉義市": (23.4801, 120.4491),
    "新竹縣": (24.8387, 121.0177),
    "苗栗縣": (24.5602, 120.8214),
    "彰化縣": (24.0759, 120.5440),
    "南投縣": (23.9609, 120.9719),
    "雲林縣": (23.7092, 120.4313),
    "嘉義縣": (23.4518, 120.2555),
    "屏東縣": (22.5519, 120.5488),
    "宜蘭縣": (24.7021, 121.7378),
    "花蓮縣": (23.9872, 121.6015),
    "臺東縣": (22.7972, 121.0714),
    "澎湖縣": (23.5711, 119.5793),
    "金門縣": (24.4321, 118.3171),
    "連江縣": (26.1602, 119.9517),
}

ITEM_STATUSES = {"active", "matched", "completed", "cancelled"}
MATCH_STATUSES = {"active", "completed", "cancelled"}
REQUEST_STATUSES = {"pending", "accepted", "rejected", "cancelled"}
SWIPE_DIRECTIONS = {"left", "right", "skip"}


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    full_name = Column(String(100), default="")
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    dorm = Column(String(80), default="")
    avatar_url = Column(String(255), default="")
    rating = Column(Float, default=0.0, index=True)
    completed_trades = Column(Integer, default=0)
    bio = Column(String(500), default="")
    email_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id", cascade="all, delete-orphan")

    def update_rating(self, score: int) -> None:
        if not 1 <= score <= 5:
            raise ValueError("評分必須介於 1 到 5 分")
        total = self.rating * self.completed_trades + score
        self.completed_trades += 1
        self.rating = round(total / self.completed_trades, 2)


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(10), nullable=False, index=True)
    description = Column(Text, default="")
    location = Column(String(100), default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(255), default="")
    seeking_categories = Column(String(120), default="")
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="items")

    def set_status(self, status: str) -> None:
        if status not in ITEM_STATUSES:
            raise ValueError(f"不支援的物品狀態: {status}")
        self.status = status

    @property
    def seeking_list(self) -> list[str]:
        return [part for part in self.seeking_categories.split(",") if part]

    def set_seeking_list(self, categories: list[str]) -> None:
        self.seeking_categories = ",".join(categories)


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_user_item_swipe"),)

    swipe_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False, index=True)
    direction = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    item = relationship("Item")


class TradeRequest(Base):
    __tablename__ = "trade_requests"
    __table_args__ = (UniqueConstraint("requester_id", "offer_item_id", "target_item_id", name="uq_trade_request_items"),)

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    requester_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    offer_item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False, index=True)
    target_item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="pending", index=True)
    message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

    requester = relationship("User", foreign_keys=[requester_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    offer_item = relationship("Item", foreign_keys=[offer_item_id])
    target_item = relationship("Item", foreign_keys=[target_item_id])
    match = relationship("Match")


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("item_a_id", "item_b_id", name="uq_match_items"),)

    match_id = Column(Integer, primary_key=True, autoincrement=True)
    user_a_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    item_a_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    item_b_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_a = relationship("User", foreign_keys=[user_a_id])
    user_b = relationship("User", foreign_keys=[user_b_id])
    item_a = relationship("Item", foreign_keys=[item_a_id])
    item_b = relationship("Item", foreign_keys=[item_b_id])
    chat_room = relationship("ChatRoom", back_populates="match", uselist=False, cascade="all, delete-orphan")

    def other_user_id(self, user_id: int) -> int:
        return self.user_b_id if user_id == self.user_a_id else self.user_a_id


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    chat_room_id = Column(Integer, primary_key=True, autoincrement=True)
    user_a_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="chat_room")
    messages = relationship("Message", back_populates="chat_room", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.chat_room_id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("match_id", "reviewer_id", name="uq_match_reviewer"),)

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.match_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id])
    match = relationship("Match")
