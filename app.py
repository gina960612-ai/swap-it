#python -m streamlit run app.py
from __future__ import annotations

from html import escape

import streamlit as st

try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None

from database import category_options, get_session, init_db, seed_demo_data
from models import CATEGORIES, Item, Match, Review, TAIWAN_LOCATIONS, TradeRequest, User
from services import (
    accept_trade_request,
    active_user_items,
    cancel_match,
    complete_match,
    create_item,
    create_trade_request,
    delete_item,
    display_account,
    distance_km,
    get_recommendations,
    get_user_review,
    incoming_trade_requests,
    login_user,
    notification_counts,
    outgoing_trade_requests,
    record_swipe,
    register_user,
    reject_trade_request,
    review_match,
    search_items,
    send_message,
    user_history_matches,
    user_matches,
)


st.set_page_config(page_title="SwapIt 校園交換", page_icon="S", layout="wide")


STATUS_TEXT = {
    "active": "交換中",
    "matched": "已配對",
    "completed": "已完成",
    "cancelled": "已取消",
}

REQUEST_STATUS_TEXT = {
    "pending": "等待對方回覆",
    "accepted": "已接受",
    "rejected": "已拒絕",
    "cancelled": "已取消",
}


def local_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; max-width: 1180px;}
        .swap-card {
            border: 1px solid #d9ded9;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
            min-height: 210px;
        }
        .muted {color: #66706a; font-size: 0.92rem;}
        .request-box {
            border: 1px solid #d9ded9;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            margin-bottom: 14px;
        }
        .chat-list-title {
            font-weight: 700;
            margin-bottom: 8px;
        }
        .chat-list-note {
            color: #66706a;
            font-size: 0.88rem;
            margin-bottom: 12px;
        }
        div.stButton > button {
            white-space: pre-wrap;
            height: auto;
            min-height: 2.75rem;
            text-align: left;
            line-height: 1.35;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def db():
    if "db" not in st.session_state:
        init_db()
        st.session_state.db = get_session()
        seed_demo_data(st.session_state.db)
    return st.session_state.db


def current_user() -> User | None:
    user_id = st.session_state.get("user_id")
    return db().get(User, user_id) if user_id else None


def category_label(code: str) -> str:
    return CATEGORIES.get(code, code)


def location_coords(location_name: str) -> tuple[float | None, float | None]:
    return TAIWAN_LOCATIONS.get(location_name, (None, None))


def current_coords() -> tuple[float | None, float | None]:
    return st.session_state.get("current_latitude"), st.session_state.get("current_longitude")


def save_current_location(location_name: str, latitude: float | None, longitude: float | None) -> None:
    st.session_state.current_location_name = location_name
    st.session_state.current_latitude = latitude
    st.session_state.current_longitude = longitude


def browser_location_button() -> None:
    if get_geolocation is None:
        st.sidebar.caption("若要自動定位，可安裝 `streamlit-js-eval`；目前先使用手動縣市。")
        return

    if st.sidebar.button("使用瀏覽器目前位置"):
        st.session_state.ask_browser_location = True

    if st.session_state.get("ask_browser_location"):
        try:
            location = get_geolocation()
        except Exception:
            location = None
        coords = (location or {}).get("coords", {})
        latitude = coords.get("latitude")
        longitude = coords.get("longitude")
        if latitude is not None and longitude is not None:
            save_current_location("瀏覽器定位", float(latitude), float(longitude))
            st.session_state.ask_browser_location = False
            st.sidebar.success("已取得目前位置")
        else:
            st.sidebar.info("請允許瀏覽器定位；若沒有反應，可改用手動縣市。")


def login_screen() -> None:
    st.title("SwapIt 校園交換")
    st.caption("用自己的物品向對方提出交換請求，對方接受後才開啟聊天。")

    login_tab, register_tab, demo_tab = st.tabs(["登入", "建立帳號", "示範帳號"])
    with login_tab:
        account_name = st.text_input("帳號名稱", value="alex")
        password = st.text_input("密碼", type="password", value="password")
        if st.button("登入", type="primary", use_container_width=True):
            user = login_user(db(), account_name, password)
            if user:
                st.session_state.user_id = user.user_id
                st.rerun()
            st.error("帳號或密碼不正確。")

    with register_tab:
        new_account = st.text_input("帳號名稱（全英，可含數字或底線）")
        new_password = st.text_input("密碼", type="password")
        confirm_password = st.text_input("確認密碼", type="password")
        nickname = st.text_input("暱稱（其他使用者看到的名字）")
        if st.button("建立帳號", use_container_width=True):
            try:
                user = register_user(db(), new_account, new_password, confirm_password, nickname)
                st.session_state.user_id = user.user_id
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    with demo_tab:
        st.info("可以直接用下面帳號測試，密碼都是 `password`。")
        st.write("alex / password")
        st.write("mina / password")
        st.write("jay / password")


def sidebar(user: User) -> str:
    incoming_count, rejected_count = notification_counts(db(), user.user_id)
    st.sidebar.title("SwapIt")
    st.sidebar.write(f"登入身分：**{user.name}**")
    st.sidebar.caption(f"帳號：{display_account(user)}")
    st.sidebar.caption(f"評分 {user.rating:.1f} / 已完成 {user.completed_trades} 次交換")
    if incoming_count or rejected_count:
        st.sidebar.warning(f"通知：{incoming_count} 個待回覆請求，{rejected_count} 個請求被拒絕")

    st.sidebar.divider()
    st.sidebar.subheader("目前位置")
    browser_location_button()
    default_location = st.session_state.get("current_location_name", "臺南市")
    manual_location = st.sidebar.selectbox(
        "手動選擇縣市",
        list(TAIWAN_LOCATIONS.keys()),
        index=list(TAIWAN_LOCATIONS.keys()).index(default_location) if default_location in TAIWAN_LOCATIONS else 4,
    )
    if st.sidebar.button("套用手動縣市", use_container_width=True):
        latitude, longitude = location_coords(manual_location)
        save_current_location(manual_location, latitude, longitude)
        st.sidebar.success(f"目前位置：{manual_location}")

    current_name = st.session_state.get("current_location_name", "尚未設定")
    st.sidebar.caption(f"推薦會優先顯示靠近「{current_name}」的物品。")

    st.sidebar.divider()
    page = st.sidebar.radio("功能", ["瀏覽物品", "我的物品", "交換請求與聊天", "歷史交易", "個人資料"])
    if st.sidebar.button("登出"):
        st.session_state.user_id = None
        st.rerun()
    return page


def distance_text(item: Item) -> str:
    latitude, longitude = current_coords()
    distance = distance_km(latitude, longitude, item.latitude, item.longitude)
    if distance is None:
        return "距離未知"
    if distance < 1:
        return f"約 {distance * 1000:.0f} 公尺"
    return f"約 {distance:.1f} 公里"


def item_card(item: Item, score: float | None = None, score_label: str = "推薦分數") -> None:
    score_line = f"<div class='muted'>{escape(score_label)}：{score:.1f} · {distance_text(item)}</div>" if score is not None else ""
    image_line = (
        f"<img src='{escape(item.image_url)}' style='width: 100%; max-height: 260px; object-fit: cover; border-radius: 8px; margin: 10px 0;' />"
        if item.image_url
        else ""
    )
    st.markdown(
        "\n".join(
            [
                '<div class="swap-card">',
                f"<h3>{escape(item.name)}</h3>",
                f"<div class='muted'>{escape(category_label(item.category))} · {escape(item.location or '縣市未設定')} · {escape(STATUS_TEXT.get(item.status, item.status))}</div>",
                score_line,
                image_line,
                f"<p>{escape(item.description or '尚未填寫描述。')}</p>",
                f"<div class='muted'>物主：{escape(item.owner.name)} · 評分 {item.owner.rating:.1f}</div>",
                "</div>",
            ]
        ),
        unsafe_allow_html=True,
    )


def offer_request_actions(user: User, target_item: Item, key_prefix: str) -> None:
    my_items = active_user_items(db(), user.user_id)
    if not my_items:
        st.info("你需要先在「我的物品」刊登至少一個交換中的物品，才能送出交換請求。")
        return

    offer_item = st.selectbox(
        "選擇你要拿來交換的物品",
        my_items,
        format_func=lambda item: f"{item.name}（{category_label(item.category)}，{item.location or '縣市未設定'}）",
        key=f"{key_prefix}_offer_{target_item.item_id}",
    )
    message = st.text_input("給對方的留言（可不填）", key=f"{key_prefix}_message_{target_item.item_id}")

    left, right = st.columns(2)
    with left:
        if st.button("不感興趣", use_container_width=True, key=f"{key_prefix}_left_{target_item.item_id}"):
            record_swipe(db(), user.user_id, target_item.item_id, "left")
            st.rerun()
    with right:
        if st.button("有興趣", type="primary", use_container_width=True, key=f"{key_prefix}_request_{target_item.item_id}"):
            try:
                create_trade_request(db(), user.user_id, offer_item.item_id, target_item.item_id, message)
                st.success(f"已送出：你想用「{offer_item.name}」交換「{target_item.name}」。")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


def browse_page(user: User) -> None:
    st.header("瀏覽物品")
    st.caption("找到想要的物品後，請選一個自己的物品送出交換請求；對方接受後才會開啟聊天。")
    latitude, longitude = current_coords()

    with st.container(border=True):
        st.subheader("搜尋物品")
        query = st.text_input("輸入物品名稱、分類、描述、縣市或物主暱稱", placeholder="例如：桌燈、電子產品、臺南市")
        if query.strip():
            results = search_items(db(), user.user_id, query, limit=20, current_latitude=latitude, current_longitude=longitude)
            if not results:
                st.info("沒有找到符合的物品，可以換個關鍵字試試。")
                return
            st.caption(f"找到 {len(results)} 筆結果，已依符合程度與距離排序。")
            for index, (item, score) in enumerate(results, start=1):
                st.markdown(f"#### 搜尋結果 {index}")
                item_card(item, score, score_label="排序分數")
                offer_request_actions(user, item, key_prefix=f"search_{index}")
            return

    st.subheader("推薦物品")
    recommendations = get_recommendations(db(), user.user_id, limit=1, current_latitude=latitude, current_longitude=longitude)
    if not recommendations:
        st.info("目前沒有新的推薦。你可以新增物品、換一個位置，或查看已送出的交換請求。")
        return

    item, score = recommendations[0]
    item_card(item, score)
    offer_request_actions(user, item, key_prefix="recommendation")


def my_items_page(user: User) -> None:
    st.header("我的物品")
    with st.expander("新增物品", expanded=True):
        categories = category_options()
        name = st.text_input("物品名稱")
        category = st.selectbox("分類", list(categories.keys()), format_func=lambda code: categories[code])
        description = st.text_area("物品描述", height=90)
        location = st.selectbox("物品所在縣市", list(TAIWAN_LOCATIONS.keys()), index=4)
        image_url = st.text_input("圖片網址（可不填）")
        if st.button("刊登物品", type="primary"):
            try:
                latitude, longitude = location_coords(location)
                create_item(db(), user.user_id, name, category, description, location, [], image_url, latitude, longitude)
                st.success("物品已刊登。")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    items = db().query(Item).filter(Item.owner_id == user.user_id).order_by(Item.created_at.desc()).all()
    if not items:
        st.info("你還沒有刊登任何物品。")
        return
    for item in items:
        c1, c2 = st.columns([4, 1])
        with c1:
            item_card(item)
        with c2:
            st.metric("狀態", STATUS_TEXT.get(item.status, item.status))
            if item.status == "active":
                if st.button("刪除", use_container_width=True, key=f"delete_item_{item.item_id}"):
                    try:
                        delete_item(db(), user.user_id, item.item_id)
                        st.success("物品已刪除。")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            else:
                st.caption("已有交易紀錄，不能刪除")


def request_sentence(request: TradeRequest, viewer_id: int) -> str:
    if request.receiver_id == viewer_id:
        return f"{request.requester.name} 想用「{request.offer_item.name}」交換你的「{request.target_item.name}」"
    return f"你想用「{request.offer_item.name}」交換 {request.receiver.name} 的「{request.target_item.name}」"


def trade_request_card(request: TradeRequest, viewer_id: int) -> None:
    st.markdown(
        "\n".join(
            [
                '<div class="request-box">',
                f"<strong>{escape(request_sentence(request, viewer_id))}</strong>",
                f"<div class='muted'>狀態：{escape(REQUEST_STATUS_TEXT.get(request.status, request.status))}</div>",
                f"<div class='muted'>提出時間：{request.created_at.strftime('%Y-%m-%d %H:%M')}</div>",
                f"<p>{escape(request.message or '沒有留言')}</p>",
                "</div>",
            ]
        ),
        unsafe_allow_html=True,
    )


def match_items_for_user(match: Match, user_id: int) -> tuple[Item, Item]:
    mine = match.item_a if match.item_a.owner_id == user_id else match.item_b
    theirs = match.item_b if match.item_a.owner_id == user_id else match.item_a
    return mine, theirs


def match_title(match: Match, user_id: int) -> str:
    mine, theirs = match_items_for_user(match, user_id)
    return f"{mine.name} <-> {theirs.name}"


def chat_list_label(match: Match, user_id: int) -> str:
    mine, theirs = match_items_for_user(match, user_id)
    other = db().get(User, match.other_user_id(user_id))
    return "\n".join(
        [
            f"對方：{other.name}",
            f"我的物品：{mine.name}",
            f"對方物品：{theirs.name}",
            f"狀態：{STATUS_TEXT.get(match.status, match.status)}",
        ]
    )


def incoming_requests_view(user: User) -> None:
    requests = incoming_trade_requests(db(), user.user_id)
    if not requests:
        st.info("目前沒有等待你回覆的交換請求。")
        return
    for request in requests:
        trade_request_card(request, user.user_id)
        left, right = st.columns(2)
        with left:
            if st.button("接受，進入聊天", type="primary", use_container_width=True, key=f"accept_{request.request_id}"):
                try:
                    accept_trade_request(db(), request.request_id, user.user_id)
                    st.success("已接受交換請求，聊天室已建立。")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        with right:
            if st.button("不接受", use_container_width=True, key=f"reject_{request.request_id}"):
                try:
                    reject_trade_request(db(), request.request_id, user.user_id)
                    st.success("已拒絕交換請求，對方會在通知中看到結果。")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))


def outgoing_requests_view(user: User) -> None:
    requests = outgoing_trade_requests(db(), user.user_id)
    if not requests:
        st.info("你還沒有送出任何交換請求。")
        return
    for request in requests:
        trade_request_card(request, user.user_id)
        if request.status == "accepted":
            st.success("對方已接受，請到「聊天室」分頁聯絡。")
        elif request.status == "rejected":
            st.warning("對方已拒絕這個交換請求。")


def chat_view(user: User) -> None:
    matches = user_matches(db(), user.user_id)
    if not matches:
        st.info("目前沒有已接受的交換。接受交換請求後，聊天室會出現在這裡。")
        return

    match_ids = {match.match_id for match in matches}
    selected_id = st.session_state.get("selected_chat_match_id")
    if selected_id not in match_ids:
        selected_id = matches[0].match_id
        st.session_state.selected_chat_match_id = selected_id

    list_col, chat_col = st.columns([1, 2.4], gap="large")
    with list_col:
        st.markdown("<div class='chat-list-title'>聊天室</div>", unsafe_allow_html=True)
        st.markdown("<div class='chat-list-note'>點選一個聊天室開始查看對話。</div>", unsafe_allow_html=True)
        for match_option in matches:
            label = chat_list_label(match_option, user.user_id)
            if st.button(label, use_container_width=True, key=f"chat_pick_{match_option.match_id}"):
                st.session_state.selected_chat_match_id = match_option.match_id
                st.rerun()

    with chat_col:
        match = db().get(Match, st.session_state.selected_chat_match_id)
        other = db().get(User, match.other_user_id(user.user_id))
        mine, theirs = match_items_for_user(match, user.user_id)
        st.subheader(f"與 {other.name} 的聊天室")
        st.caption(f"我的物品：{mine.name} · 對方物品：{theirs.name} · 對方評分 {other.rating:.1f}")

        action_cols = st.columns(3)
        with action_cols[0]:
            if match.status == "active" and st.button("標記完成", use_container_width=True):
                complete_match(db(), match.match_id)
                st.rerun()
        with action_cols[1]:
            if match.status == "active" and st.button("取消配對", use_container_width=True):
                cancel_match(db(), match.match_id)
                st.rerun()
        with action_cols[2]:
            st.markdown(f"**狀態：** {STATUS_TEXT.get(match.status, match.status)}")

        st.divider()
        room = match.chat_room
        for message in (room.messages if room else []):
            sender = "你" if message.sender_id == user.user_id else message.sender.name
            with st.chat_message("user" if message.sender_id == user.user_id else "assistant"):
                st.write(f"**{sender}**")
                st.write(message.content)

        if match.status == "active":
            content = st.chat_input("輸入訊息")
            if content:
                send_message(db(), match.match_id, user.user_id, content)
                st.rerun()

        if match.status == "completed":
            st.divider()
            st.subheader("評價這次交換")
            already_reviewed = db().query(Review).filter(Review.match_id == match.match_id, Review.reviewer_id == user.user_id).first()
            if already_reviewed:
                st.success("你已經評價過這次交換。")
            else:
                rating = st.slider("評分", 1, 5, 5)
                comment = st.text_area("留言", height=80)
                if st.button("送出評價"):
                    try:
                        review_match(db(), match.match_id, user.user_id, rating, comment)
                        st.success("評價已送出。")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))


def requests_and_chat_page(user: User) -> None:
    st.header("交換請求與聊天")
    incoming_count, rejected_count = notification_counts(db(), user.user_id)
    st.caption(f"收到待回覆：{incoming_count} · 被拒絕通知：{rejected_count}")
    incoming_tab, outgoing_tab, chat_tab = st.tabs(["收到的請求", "我的請求通知", "聊天室"])
    with incoming_tab:
        incoming_requests_view(user)
    with outgoing_tab:
        outgoing_requests_view(user)
    with chat_tab:
        chat_view(user)


def profile_page(user: User) -> None:
    st.header("個人資料")
    col1, col2, col3 = st.columns(3)
    col1.metric("評分", f"{user.rating:.1f}")
    col2.metric("完成交換", user.completed_trades)
    col3.metric("刊登物品", len(user.items))
    st.write(f"**帳號名稱：** {display_account(user)}")
    st.write(f"**暱稱：** {user.name}")
    st.write(user.bio or "尚未填寫自我介紹。")


def history_page(user: User) -> None:
    st.header("歷史交易")
    st.caption("查看所有已完成和已取消的交易紀錄，並評分已完成的交易。")
    
    history_matches = user_history_matches(db(), user.user_id)
    if not history_matches:
        st.info("目前沒有歷史交易紀錄。")
        return
    
    # 分別篩選已完成和已取消的交易
    completed_matches = [m for m in history_matches if m.status == "completed"]
    cancelled_matches = [m for m in history_matches if m.status == "cancelled"]
    
    # 已完成的交易
    if completed_matches:
        st.subheader("✅ 已完成的交易")
        for match in completed_matches:
            mine, theirs = match_items_for_user(match, user.user_id)
            other = db().get(User, match.other_user_id(user.user_id))
            user_review = get_user_review(db(), match.match_id, user.user_id)
            other_review = get_user_review(db(), match.match_id, match.other_user_id(user.user_id))
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{escape(mine.name)}** ↔ **{escape(theirs.name)}**")
                    st.caption(f"對方：{escape(other.name)} · 完成時間：{match.completed_at.strftime('%Y-%m-%d %H:%M')}")
                    st.caption(f"對方評分：{other.rating:.1f}")
                
                with col2:
                    if user_review:
                        st.success(f"⭐ 你的評分：{user_review.rating}分")
                        if user_review.comment:
                            st.caption(f"留言：{escape(user_review.comment)}")
                    else:
                        st.info("尚未評分")
                
                # 評分按鈕
                if not user_review:
                    st.divider()
                    rating = st.slider(
                        "評分",
                        1, 5, 5,
                        key=f"history_rating_{match.match_id}"
                    )
                    comment = st.text_input(
                        "評論（可選）",
                        key=f"history_comment_{match.match_id}"
                    )
                    if st.button(
                        "送出評分",
                        key=f"history_submit_{match.match_id}",
                        use_container_width=True
                    ):
                        try:
                            review_match(db(), match.match_id, user.user_id, rating, comment)
                            st.success("評分已送出！")
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
    
    # 已取消的交易
    if cancelled_matches:
        st.subheader("❌ 已取消的交易")
        for match in cancelled_matches:
            mine, theirs = match_items_for_user(match, user.user_id)
            other = db().get(User, match.other_user_id(user.user_id))
            
            with st.container(border=True):
                st.markdown(f"**{escape(mine.name)}** ↔ **{escape(theirs.name)}**")
                st.caption(f"對方：{escape(other.name)} · 取消時間：{match.updated_at.strftime('%Y-%m-%d %H:%M')}")


def main() -> None:
    local_css()
    user = current_user()
    if not user:
        login_screen()
        return

    page = sidebar(user)
    if page == "瀏覽物品":
        browse_page(user)
    elif page == "我的物品":
        my_items_page(user)
    elif page == "交換請求與聊天":
        requests_and_chat_page(user)
    elif page == "歷史交易":
        history_page(user)
    else:
        profile_page(user)


if __name__ == "__main__":
    main()
