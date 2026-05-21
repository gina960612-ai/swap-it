import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Item, Match, User
from services import (
    accept_trade_request,
    create_item,
    create_trade_request,
    delete_item,
    get_recommendations,
    incoming_trade_requests,
    login_user,
    outgoing_trade_requests,
    reject_trade_request,
    register_user,
    review_match,
    search_items,
    send_message,
    update_item,
)


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    return Session()


def test_register_and_login_user():
    db = make_db()
    user = register_user(db, "Kai", "secret1", "secret1", "Kai")

    assert user.user_id is not None
    assert login_user(db, "kai", "secret1").user_id == user.user_id
    assert login_user(db, "kai", "wrong") is None


def test_recommendations_prioritize_location():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    mina = register_user(db, "Mina", "secret1", "secret1", "Mina")
    jay = register_user(db, "Jay", "secret1", "secret1", "Jay")
    create_item(db, kai.user_id, "Novel", "BOO", "Good book", "Tainan", [], latitude=23.0, longitude=120.2)
    near = create_item(db, mina.user_id, "Keyboard", "ELE", "Mechanical", "Tainan", [], latitude=23.0, longitude=120.2)
    far = create_item(db, jay.user_id, "Jacket", "CLO", "Warm", "Taipei", [], latitude=25.0, longitude=121.5)

    recommendations = get_recommendations(db, kai.user_id, current_latitude=23.0, current_longitude=120.2)

    assert recommendations[0][0].item_id == near.item_id
    assert recommendations[-1][0].item_id == far.item_id
    assert recommendations[0][1] > recommendations[-1][1]


def test_trade_request_reject_notifies_requester_without_match():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    mina = register_user(db, "Mina", "secret1", "secret1", "Mina")
    book = create_item(db, kai.user_id, "Book", "BOO", "Freshman text", "Tainan", [])
    keyboard = create_item(db, mina.user_id, "Keyboard", "ELE", "Compact", "Tainan", [])

    request = create_trade_request(db, kai.user_id, book.item_id, keyboard.item_id, "Can we trade?")
    assert incoming_trade_requests(db, mina.user_id)[0].request_id == request.request_id

    reject_trade_request(db, request.request_id, mina.user_id)
    outgoing = outgoing_trade_requests(db, kai.user_id)[0]

    assert outgoing.status == "rejected"
    assert db.query(Match).count() == 0
    assert db.get(Item, book.item_id).status == "active"
    assert db.get(Item, keyboard.item_id).status == "active"


def test_delete_active_item_cancels_pending_requests():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    mina = register_user(db, "Mina", "secret1", "secret1", "Mina")
    book = create_item(db, kai.user_id, "Book", "BOO", "Freshman text", "Tainan", [])
    keyboard = create_item(db, mina.user_id, "Keyboard", "ELE", "Compact", "Tainan", [])
    request = create_trade_request(db, kai.user_id, book.item_id, keyboard.item_id)

    delete_item(db, kai.user_id, book.item_id)

    assert db.get(Item, book.item_id) is None
    assert outgoing_trade_requests(db, kai.user_id)[0].status == "cancelled"
    assert db.get(Item, keyboard.item_id).status == "active"


def test_update_active_item_changes_fields():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    item = create_item(db, kai.user_id, "Lamp", "ELE", "Old lamp", "Tainan", [], image_url="https://old.example/lamp.jpg", latitude=23.0, longitude=120.2)

    updated = update_item(
        db,
        kai.user_id,
        item.item_id,
        "Desk Lamp",
        "ELE",
        "New and improved",
        "Kaohsiung",
        "https://new.example/lamp.jpg",
        22.6,
        120.3,
    )

    assert updated.name == "Desk Lamp"
    assert updated.description == "New and improved"
    assert updated.location == "Kaohsiung"
    assert updated.image_url == "https://new.example/lamp.jpg"
    assert updated.latitude == 22.6
    assert updated.longitude == 120.3


def test_update_item_requires_active_status():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    item = create_item(db, kai.user_id, "Lamp", "ELE", "Old lamp", "Tainan", [])
    item.status = "matched"
    db.commit()

    with pytest.raises(ValueError):
        update_item(db, kai.user_id, item.item_id, "Desk Lamp", "ELE", "New description", "Kaohsiung", "", 22.6, 120.3)


def test_accept_trade_request_creates_match_and_chat():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    mina = register_user(db, "Mina", "secret1", "secret1", "Mina")
    book = create_item(db, kai.user_id, "Book", "BOO", "Freshman text", "Tainan", [])
    keyboard = create_item(db, mina.user_id, "Keyboard", "ELE", "Compact", "Tainan", [])
    request = create_trade_request(db, kai.user_id, book.item_id, keyboard.item_id)

    match = accept_trade_request(db, request.request_id, mina.user_id)

    assert isinstance(match, Match)
    assert db.get(Item, book.item_id).status == "matched"
    assert db.get(Item, keyboard.item_id).status == "matched"
    assert match.chat_room is not None
    assert outgoing_trade_requests(db, kai.user_id)[0].status == "accepted"

    message = send_message(db, match.match_id, kai.user_id, "Want to trade tomorrow?")
    assert message.content == "Want to trade tomorrow?"


def test_review_completed_match_updates_rating_once():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    mina = register_user(db, "Mina", "secret1", "secret1", "Mina")
    book = create_item(db, kai.user_id, "Book", "BOO", "Freshman text", "Tainan", [])
    keyboard = create_item(db, mina.user_id, "Keyboard", "ELE", "Compact", "Tainan", [])
    request = create_trade_request(db, kai.user_id, book.item_id, keyboard.item_id)
    match = accept_trade_request(db, request.request_id, mina.user_id)

    review = review_match(db, match.match_id, kai.user_id, 5, "Smooth trade")
    reviewed_user = db.get(User, mina.user_id)

    assert review.rating == 5
    assert reviewed_user.rating == 5
    assert reviewed_user.completed_trades == 1


def test_search_items_sorts_by_relevance_then_location():
    db = make_db()
    kai = register_user(db, "Kai", "secret1", "secret1", "Kai")
    mina = register_user(db, "Mina", "secret1", "secret1", "Mina")
    jay = register_user(db, "Jay", "secret1", "secret1", "Jay")
    create_item(db, kai.user_id, "Pen", "LIF", "Offer item", "Tainan", [], latitude=23.0, longitude=120.2)
    exact = create_item(db, mina.user_id, "Desk lamp", "ELE", "Bright light", "Tainan", [], latitude=23.0, longitude=120.2)
    partial = create_item(db, jay.user_id, "Desk organizer", "LIF", "Has a tiny lamp clip", "Taipei", [], latitude=25.0, longitude=121.5)
    create_item(db, jay.user_id, "Rice cooker", "APP", "Small cooker", "Tainan", [], latitude=23.0, longitude=120.2)

    results = search_items(db, kai.user_id, "lamp", current_latitude=23.0, current_longitude=120.2)

    assert [item.item_id for item, score in results] == [exact.item_id, partial.item_id]
    assert results[0][1] > results[1][1]
