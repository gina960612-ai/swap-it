from __future__ import annotations

import math
import re
from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from models import CATEGORIES, ChatRoom, Item, Match, Message, Review, Swipe, TradeRequest, User


ACCOUNT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,19}$")
LOCAL_ACCOUNT_DOMAIN = "swapit.local"


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def account_to_email(account_name: str) -> str:
    return f"{account_name.strip().lower()}@{LOCAL_ACCOUNT_DOMAIN}"


def display_account(user: User) -> str:
    if user.email.endswith(f"@{LOCAL_ACCOUNT_DOMAIN}") or user.email.endswith("@swapit.demo"):
        return user.email.split("@", 1)[0]
    return user.email


def register_user(db: Session, account_name: str, password: str, confirm_password: str, nickname: str, full_name: str = "") -> User:
    account_name = account_name.strip()
    nickname = nickname.strip()
    full_name = full_name.strip()

    if not ACCOUNT_RE.fullmatch(account_name):
        raise ValueError("帳號名稱需為 3-20 個英文字母、數字或底線，且第一個字必須是英文字母")
    if len(password) < 6:
        raise ValueError("密碼至少需要 6 個字元")
    if password != confirm_password:
        raise ValueError("兩次輸入的密碼不一致")
    if not nickname:
        raise ValueError("請輸入暱稱")

    email = account_to_email(account_name)
    if db.query(User).filter(User.email == email).first():
        raise ValueError("這個帳號名稱已經被使用")

    user = User(name=nickname, full_name=full_name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, account_name: str, password: str) -> User | None:
    account_name = account_name.strip().lower()
    lookup = account_name if "@" in account_name else account_to_email(account_name)
    user = db.query(User).filter(User.email == lookup).first()
    if user is None and "@" not in account_name:
        user = db.query(User).filter(User.email == f"{account_name}@swapit.demo").first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def update_user_profile(db: Session, user_id: int, name: str, full_name: str, dorm: str, bio: str, avatar_url: str = "") -> User:
    name = name.strip()
    full_name = full_name.strip()
    dorm = dorm.strip()
    bio = bio.strip()
    avatar_url = avatar_url.strip()

    if not name:
        raise ValueError("請輸入暱稱")

    user = db.get(User, user_id)
    if user is None:
        raise ValueError("無法找到此使用者")

    user.name = name
    user.full_name = full_name
    user.dorm = dorm
    user.bio = bio
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user


def create_item(
    db: Session,
    owner_id: int,
    name: str,
    category: str,
    description: str,
    location: str,
    seeking_categories: list[str] | None = None,
    image_url: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
) -> Item:
    if not name.strip():
        raise ValueError("請輸入物品名稱")
    item = Item(
        owner_id=owner_id,
        name=name.strip(),
        category=category,
        description=description.strip(),
        location=location.strip(),
        latitude=latitude,
        longitude=longitude,
        image_url=image_url.strip(),
        status="active",
    )
    item.set_seeking_list(seeking_categories or [])
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def active_user_items(db: Session, user_id: int) -> list[Item]:
    return db.query(Item).filter(Item.owner_id == user_id, Item.status == "active").order_by(Item.created_at.desc()).all()


def update_item(
    db: Session,
    owner_id: int,
    item_id: int,
    name: str,
    category: str,
    description: str,
    location: str,
    image_url: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
) -> Item:
    if not name.strip():
        raise ValueError("請輸入物品名稱")

    item = db.get(Item, item_id)
    if not item or item.owner_id != owner_id:
        raise ValueError("找不到這個物品，或你沒有權限編輯")
    if item.status != "active":
        raise ValueError("已配對、已完成或已取消的物品不能編輯")

    item.name = name.strip()
    item.category = category
    item.description = description.strip()
    item.location = location.strip()
    item.latitude = latitude
    item.longitude = longitude
    item.image_url = image_url.strip()

    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, owner_id: int, item_id: int) -> None:
    item = db.get(Item, item_id)
    if not item or item.owner_id != owner_id:
        raise ValueError("找不到這個物品，或你沒有權限刪除")
    if item.status != "active":
        raise ValueError("已配對、已完成或已取消的物品不能直接刪除，避免影響交易紀錄")

    pending_requests = (
        db.query(TradeRequest)
        .filter(
            or_(TradeRequest.offer_item_id == item_id, TradeRequest.target_item_id == item_id),
            TradeRequest.status == "pending",
        )
        .all()
    )
    for request in pending_requests:
        request.status = "cancelled"
        request.responded_at = datetime.utcnow()

    db.delete(item)
    db.commit()


def distance_km(lat_a: float | None, lon_a: float | None, lat_b: float | None, lon_b: float | None) -> float | None:
    if None in (lat_a, lon_a, lat_b, lon_b):
        return None
    radius = 6371.0
    phi_a = math.radians(float(lat_a))
    phi_b = math.radians(float(lat_b))
    delta_phi = math.radians(float(lat_b) - float(lat_a))
    delta_lambda = math.radians(float(lon_b) - float(lon_a))
    hav = math.sin(delta_phi / 2) ** 2 + math.cos(phi_a) * math.cos(phi_b) * math.sin(delta_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(hav), math.sqrt(1 - hav))


def location_bonus(distance: float | None) -> float:
    if distance is None:
        return 0.0
    if distance <= 0.2:
        return 3.0
    if distance <= 0.5:
        return 2.2
    if distance <= 1.0:
        return 1.4
    if distance <= 2.0:
        return 0.7
    return 0.0


def recommendation_score(
    current_user: User,
    candidate: Item,
    current_latitude: float | None = None,
    current_longitude: float | None = None,
) -> float:
    my_active_items = [item for item in current_user.items if item.status == "active"]
    my_categories = {item.category for item in my_active_items}
    distance = distance_km(current_latitude, current_longitude, candidate.latitude, candidate.longitude)

    score = 0.0
    if candidate.category in my_categories:
        score += 1.0
    score += location_bonus(distance)
    score += min(candidate.owner.rating, 5.0) * 0.4
    return round(score, 2)


def _already_requested_target_ids(db: Session, user_id: int) -> set[int]:
    rows = (
        db.query(TradeRequest.target_item_id)
        .filter(TradeRequest.requester_id == user_id, TradeRequest.status.in_(["pending", "accepted"]))
        .all()
    )
    return {row.target_item_id for row in rows}


def get_recommendations(
    db: Session,
    user_id: int,
    limit: int = 20,
    current_latitude: float | None = None,
    current_longitude: float | None = None,
) -> list[tuple[Item, float]]:
    user = db.get(User, user_id)
    excluded_target_ids = _already_requested_target_ids(db, user_id)
    seen_item_ids = {row.item_id for row in db.query(Swipe.item_id).filter(Swipe.user_id == user_id).all()}
    excluded_item_ids = excluded_target_ids.union(seen_item_ids)
    candidates = (
        db.query(Item)
        .filter(Item.owner_id != user_id, Item.status == "active", ~Item.item_id.in_(excluded_item_ids or {0}))
        .all()
    )
    ranked = [(item, recommendation_score(user, item, current_latitude, current_longitude)) for item in candidates]
    ranked.sort(key=lambda pair: (pair[1], pair[0].created_at), reverse=True)
    return ranked[:limit]


def text_match_score(query: str, item: Item) -> float:
    terms = [term.strip().lower() for term in query.split() if term.strip()]
    if not terms:
        return 0.0

    fields = {
        "name": (item.name or "").lower(),
        "description": (item.description or "").lower(),
        "category": CATEGORIES.get(item.category, item.category).lower(),
        "location": (item.location or "").lower(),
        "owner": (item.owner.name or "").lower(),
    }

    score = 0.0
    for term in terms:
        if term == fields["name"]:
            score += 8.0
        if fields["name"].startswith(term):
            score += 5.0
        if term in fields["name"]:
            score += 4.0
        if term in fields["category"]:
            score += 3.0
        if term in fields["description"]:
            score += 2.0
        if term in fields["location"]:
            score += 1.5
        if term in fields["owner"]:
            score += 1.0
    return score


def search_items(
    db: Session,
    user_id: int,
    query: str,
    limit: int = 20,
    current_latitude: float | None = None,
    current_longitude: float | None = None,
) -> list[tuple[Item, float]]:
    query = query.strip()
    if not query:
        return []

    excluded_target_ids = _already_requested_target_ids(db, user_id)
    user = db.get(User, user_id)
    candidates = (
        db.query(Item)
        .filter(Item.owner_id != user_id, Item.status == "active", ~Item.item_id.in_(excluded_target_ids or {0}))
        .all()
    )
    ranked: list[tuple[Item, float]] = []
    for item in candidates:
        match_score = text_match_score(query, item)
        if match_score <= 0:
            continue
        total_score = match_score * 10 + recommendation_score(user, item, current_latitude, current_longitude)
        ranked.append((item, round(total_score, 2)))

    ranked.sort(key=lambda pair: (pair[1], pair[0].created_at), reverse=True)
    return ranked[:limit]


def create_trade_request(
    db: Session,
    requester_id: int,
    offer_item_id: int,
    target_item_id: int,
    message: str = "",
) -> TradeRequest:
    offer_item = db.get(Item, offer_item_id)
    target_item = db.get(Item, target_item_id)

    if not offer_item or not target_item:
        raise ValueError("找不到指定的物品")
    if offer_item.owner_id != requester_id:
        raise ValueError("只能用自己刊登的物品提出交換")
    if target_item.owner_id == requester_id:
        raise ValueError("不能對自己的物品提出交換")
    if offer_item.status != "active" or target_item.status != "active":
        raise ValueError("只有交換中的物品可以提出請求")

    existing = (
        db.query(TradeRequest)
        .filter(
            TradeRequest.requester_id == requester_id,
            TradeRequest.offer_item_id == offer_item_id,
            TradeRequest.target_item_id == target_item_id,
            TradeRequest.status == "pending",
        )
        .first()
    )
    if existing:
        raise ValueError("你已經送出過這個交換請求")

    request = TradeRequest(
        requester_id=requester_id,
        receiver_id=target_item.owner_id,
        offer_item_id=offer_item_id,
        target_item_id=target_item_id,
        status="pending",
        message=message.strip(),
    )
    db.add(request)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("這個交換請求已經存在") from exc
    db.refresh(request)
    return request


def incoming_trade_requests(db: Session, user_id: int) -> list[TradeRequest]:
    return (
        db.query(TradeRequest)
        .filter(TradeRequest.receiver_id == user_id, TradeRequest.status == "pending")
        .order_by(TradeRequest.created_at.desc())
        .all()
    )


def outgoing_trade_requests(db: Session, user_id: int) -> list[TradeRequest]:
    return (
        db.query(TradeRequest)
        .filter(TradeRequest.requester_id == user_id)
        .order_by(TradeRequest.updated_at.desc(), TradeRequest.created_at.desc())
        .all()
    )


def notification_counts(db: Session, user_id: int) -> tuple[int, int]:
    incoming = db.query(TradeRequest).filter(TradeRequest.receiver_id == user_id, TradeRequest.status == "pending").count()
    rejected = db.query(TradeRequest).filter(TradeRequest.requester_id == user_id, TradeRequest.status == "rejected").count()
    return incoming, rejected


def _create_match_for_items(db: Session, item_one: Item, item_two: Item) -> Match:
    item_a, item_b = sorted([item_one, item_two], key=lambda item: item.item_id)
    existing = db.query(Match).filter(Match.item_a_id == item_a.item_id, Match.item_b_id == item_b.item_id).first()
    if existing:
        return existing

    match = Match(
        user_a_id=item_a.owner_id,
        user_b_id=item_b.owner_id,
        item_a_id=item_a.item_id,
        item_b_id=item_b.item_id,
        status="active",
    )
    item_a.set_status("matched")
    item_b.set_status("matched")
    db.add(match)
    db.flush()
    db.add(ChatRoom(user_a_id=match.user_a_id, user_b_id=match.user_b_id, match_id=match.match_id))
    return match


def accept_trade_request(db: Session, request_id: int, receiver_id: int) -> Match:
    request = db.get(TradeRequest, request_id)
    if not request:
        raise ValueError("找不到交換請求")
    if request.receiver_id != receiver_id:
        raise ValueError("只有物品擁有者可以回覆這個請求")
    if request.status != "pending":
        raise ValueError("這個交換請求已經回覆過")
    if request.offer_item.status != "active" or request.target_item.status != "active":
        raise ValueError("其中一個物品已經不能交換")

    match = _create_match_for_items(db, request.offer_item, request.target_item)
    request.status = "accepted"
    request.match_id = match.match_id
    request.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(match)
    return match


def reject_trade_request(db: Session, request_id: int, receiver_id: int) -> TradeRequest:
    request = db.get(TradeRequest, request_id)
    if not request:
        raise ValueError("找不到交換請求")
    if request.receiver_id != receiver_id:
        raise ValueError("只有物品擁有者可以回覆這個請求")
    if request.status != "pending":
        raise ValueError("這個交換請求已經回覆過")

    request.status = "rejected"
    request.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(request)
    return request


def record_swipe(db: Session, user_id: int, item_id: int, direction: str) -> None:
    if direction not in {"left", "skip"}:
        raise ValueError("新的交換流程只支援略過或不感興趣")
    existing = db.query(Swipe).filter(Swipe.user_id == user_id, Swipe.item_id == item_id).first()
    if existing:
        existing.direction = direction
        existing.created_at = datetime.utcnow()
    else:
        db.add(Swipe(user_id=user_id, item_id=item_id, direction=direction))
    db.commit()


def user_matches(db: Session, user_id: int) -> list[Match]:
    return (
        db.query(Match)
        .filter(or_(Match.user_a_id == user_id, Match.user_b_id == user_id))
        .order_by(Match.updated_at.desc())
        .all()
    )


def send_message(db: Session, match_id: int, sender_id: int, content: str) -> Message:
    if not content.strip():
        raise ValueError("請輸入訊息內容")
    match = db.get(Match, match_id)
    if not match or sender_id not in {match.user_a_id, match.user_b_id}:
        raise ValueError("找不到可使用的聊天室")
    if match.status != "active":
        raise ValueError("只有進行中的配對可以聊天")

    room = db.query(ChatRoom).filter(ChatRoom.match_id == match_id).first()
    if not room:
        room = ChatRoom(user_a_id=match.user_a_id, user_b_id=match.user_b_id, match_id=match.match_id)
        db.add(room)
        db.flush()
    msg = Message(chat_room_id=room.chat_room_id, sender_id=sender_id, content=content.strip())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def complete_match(db: Session, match_id: int) -> Match:
    match = db.get(Match, match_id)
    if not match:
        raise ValueError("找不到這筆配對")
    match.status = "completed"
    match.completed_at = datetime.utcnow()
    match.item_a.set_status("completed")
    match.item_b.set_status("completed")
    db.commit()
    db.refresh(match)
    return match


def cancel_match(db: Session, match_id: int) -> Match:
    match = db.get(Match, match_id)
    if not match:
        raise ValueError("找不到這筆配對")
    match.status = "cancelled"
    match.item_a.set_status("active")
    match.item_b.set_status("active")
    db.commit()
    db.refresh(match)
    return match


def review_match(db: Session, match_id: int, reviewer_id: int, rating: int, comment: str = "") -> Review:
    if not 1 <= rating <= 5:
        raise ValueError("評分必須介於 1 到 5 分")
    match = db.get(Match, match_id)
    if not match:
        raise ValueError("找不到這筆配對")
    if match.status != "completed":
        complete_match(db, match_id)
        match = db.get(Match, match_id)

    reviewee_id = match.other_user_id(reviewer_id)
    existing = db.query(Review).filter(and_(Review.match_id == match_id, Review.reviewer_id == reviewer_id)).first()
    if existing:
        raise ValueError("你已經評價過這筆交易")

    reviewee = db.get(User, reviewee_id)
    reviewee.update_rating(rating)
    review = Review(match_id=match_id, reviewer_id=reviewer_id, reviewee_id=reviewee_id, rating=rating, comment=comment.strip())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def user_history_matches(db: Session, user_id: int) -> list[Match]:
    """獲取用戶的歷史交易（已完成和已取消的交易）"""
    return (
        db.query(Match)
        .filter(
            and_(
                or_(Match.user_a_id == user_id, Match.user_b_id == user_id),
                or_(Match.status == "completed", Match.status == "cancelled")
            )
        )
        .order_by(Match.completed_at.desc(), Match.updated_at.desc())
        .all()
    )


def get_user_review(db: Session, match_id: int, reviewer_id: int) -> Review | None:
    """獲取特定用戶對某個交易的評分"""
    return db.query(Review).filter(
        and_(Review.match_id == match_id, Review.reviewer_id == reviewer_id)
    ).first()
