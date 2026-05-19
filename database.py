from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base, CATEGORIES, Item, TAIWAN_LOCATIONS, User
from services import account_to_email, hash_password


import sys

# Safely read DATABASE_URL; if reading environment raises UnicodeDecodeError, fall back to sqlite
try:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///swapit.db")
except UnicodeDecodeError:
    print("WARNING: Could not decode DATABASE_URL from environment (UnicodeDecodeError). Falling back to sqlite:///swapit.db", file=sys.stderr)
    DATABASE_URL = "sqlite:///swapit.db"


def make_engine(database_url: str = DATABASE_URL):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    
    try:
        engine = create_engine(database_url, connect_args=connect_args)
        # Test the connection early to catch issues
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        # If any error occurs (including UnicodeDecodeError), fall back to SQLite
        print(f"WARNING: Failed to connect to {repr(database_url)}: {e}", file=sys.stderr)
        print("Falling back to SQLite at sqlite:///swapit.db", file=sys.stderr)
        fallback_url = "sqlite:///swapit.db"
        return create_engine(fallback_url, connect_args={"check_same_thread": False})


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)
    ensure_schema()


def ensure_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return
    with engine.begin() as conn:
        item_columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(items)").fetchall()}
        if "latitude" not in item_columns:
            conn.execute(text("ALTER TABLE items ADD COLUMN latitude FLOAT"))
        if "longitude" not in item_columns:
            conn.execute(text("ALTER TABLE items ADD COLUMN longitude FLOAT"))

        legacy_locations = {
            "A Dorm": "臺南市",
            "A Dorm lobby": "臺南市",
            "B Dorm": "臺南市",
            "B Dorm pantry": "臺南市",
            "Library": "臺南市",
            "Student center": "臺南市",
            "Bike parking": "臺南市",
            "宿舍A": "臺南市",
            "宿舍B": "臺南市",
            "圖書館": "臺南市",
            "學生餐廳": "臺南市",
            "體育館": "臺南市",
        }
        for old_name, new_name in legacy_locations.items():
            latitude, longitude = TAIWAN_LOCATIONS[new_name]
            conn.execute(
                text(
                    """
                    UPDATE items
                    SET latitude = :latitude, longitude = :longitude
                    WHERE location = :old_name AND (latitude IS NULL OR longitude IS NULL)
                    """
                ),
                {"latitude": latitude, "longitude": longitude, "old_name": old_name},
            )

        legacy_items = {
            "Adjustable desk lamp": ("可調式桌燈", "三段色溫 LED 桌燈，讀書很好用。", "臺南市"),
            "Calculus textbook": ("微積分課本", "內頁乾淨，有少量筆記，適合大一使用。", "臺北市"),
            "Mini rice cooker": ("迷你電鍋", "一人份小電鍋，功能正常。", "高雄市"),
            "Denim jacket": ("牛仔外套", "M 號，少穿，保存良好。", "新北市"),
            "Switch controller": ("Switch 手把", "無線手把，附 USB-C 線。", "臺中市"),
            "Road bike lights": ("腳踏車燈組", "前後燈，可 USB 充電。", "花蓮縣"),
        }
        for old_name, (new_name, description, location) in legacy_items.items():
            latitude, longitude = TAIWAN_LOCATIONS[location]
            conn.execute(
                text(
                    """
                    UPDATE items
                    SET name = :new_name,
                        description = :description,
                        location = :location,
                        latitude = :latitude,
                        longitude = :longitude
                    WHERE name = :old_name
                    """
                ),
                {
                    "old_name": old_name,
                    "new_name": new_name,
                    "description": description,
                    "location": location,
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )


def get_session() -> Session:
    init_db()
    return SessionLocal()


@contextmanager
def session_scope():
    db = get_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_demo_data(db: Session) -> None:
    if db.query(User).count() > 0:
        return

    users = [
        User(name="阿翔", email=account_to_email("alex"), password_hash=hash_password("password"), dorm="臺南市", bio="想換書和桌面小物。"),
        User(name="米娜", email=account_to_email("mina"), password_hash=hash_password("password"), dorm="高雄市", bio="準備搬宿舍，很多東西想交換。"),
        User(name="小傑", email=account_to_email("jay"), password_hash=hash_password("password"), dorm="臺中市", bio="喜歡遊戲和實用小物。"),
    ]
    db.add_all(users)
    db.flush()

    demo_items = [
        (users[0], "可調式桌燈", "FUR", "三段色溫 LED 桌燈，讀書很好用。", "臺南市"),
        (users[0], "微積分課本", "BOO", "內頁乾淨，有少量筆記，適合大一使用。", "臺北市"),
        (users[1], "迷你電鍋", "APP", "一人份小電鍋，功能正常。", "高雄市"),
        (users[1], "牛仔外套", "CLO", "M 號，少穿，保存良好。", "新北市"),
        (users[2], "Switch 手把", "GAM", "無線手把，附 USB-C 線。", "臺中市"),
        (users[2], "腳踏車燈組", "TRN", "前後燈，可 USB 充電。", "花蓮縣"),
    ]
    for owner, name, category, description, location in demo_items:
        latitude, longitude = TAIWAN_LOCATIONS.get(location, (None, None))
        db.add(
            Item(
                owner_id=owner.user_id,
                name=name,
                category=category,
                description=description,
                location=location,
                latitude=latitude,
                longitude=longitude,
            )
        )
    db.commit()


def category_options() -> dict[str, str]:
    return CATEGORIES.copy()
