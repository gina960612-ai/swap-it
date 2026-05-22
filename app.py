#python -m streamlit run app.py
from __future__ import annotations

from html import escape
import os
import base64
from uuid import uuid4

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
    update_item,
    update_user_profile,
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
        /* 📊 彩色調色盤 */
        :root {
            --primary: #7B5BA3;
            --primary-dark: #5A3F7F;
            --primary-light: #B399CC;
            --primary-lighter: #D4B5E8;
            --accent1: #FF69B4;
            --accent2: #FF6B9D;
            --bg-light: #F5F3FA;
            --bg-white: #FFFFFF;
            --text-dark: #2C2C2C;
            --border-light: #E8DDF5;
        }

        /* 強制背景顏色 */
        [data-testid="stAppViewContainer"] > div {
            background-color: #FFFFFF !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF !important;
        }
        .main {
            background-color: #FFFFFF !important;
        }
        body {
            background-color: #FFFFFF !important;
        }
        .stApp {
            background-color: #FFFFFF !important;
        }

        /* 全局樣式 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1100px !important;
        }
        body {
            background: #FFFFFF !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 16px;
            color: #2C2C2C;
        }
        .main {
            background: #FFFFFF !important;
        }
        .stApp {
            background: #FFFFFF !important;
        }
        
        /* 改善輸入框樣式 */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            border-radius: 12px;
            border: 1px solid rgba(123, 91, 163, 0.2);
            padding: 12px 16px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(123, 91, 163, 0.08);
        }
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #7B5BA3;
            box-shadow: 0 4px 12px rgba(123, 91, 163, 0.15);
            background: #ffffff;
        }

        /* 🎴 卡片樣式 (核心改版) */
        .swap-card {
            border: none;
            border-radius: 16px;
            padding: 20px;
            background: #ffffff;
            min-height: auto;
            box-shadow: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 20px;
            margin-top: 0;
        }
        .swap-card:hover {
            box-shadow: 0 8px 24px rgba(123, 91, 163, 0.12);
            transform: translateY(-2px);
        }
        .swap-card h3 {
            color: #2C2C2C;
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0 0 12px 0;
            letter-spacing: -0.3px;
        }

        /* 文字樣式 */
        .muted {
            color: #6b7280;
            font-size: 0.9rem;
            font-weight: 400;
            line-height: 1.6;
            display: block;
            margin-bottom: 8px;
        }
        
        /* 區段標題樣式 */
        h1 {
            color: #7B5BA3;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        h2 {
            color: #7B5BA3;
            font-weight: 600;
            letter-spacing: -0.3px;
            font-size: 1.5rem;
        }
        h3 {
            color: #5A3F7F;
            font-weight: 600;
            letter-spacing: -0.25px;
            font-size: 1.25rem;
        }
        h4 {
            color: #2C2C2C;
            font-weight: 600;
            font-size: 1.1rem;
        }

        /* 📋 請求框樣式 */
        .request-box {
            border: none;
            border-radius: 16px;
            padding: 18px;
            background: #FFFFFF;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
        }
        .request-box:hover {
            box-shadow: 0 2px 8px rgba(123, 91, 163, 0.08);
        }

        /* 💬 聊天列表 */
        .chat-list-title {
            font-weight: 600;
            margin-bottom: 8px;
            color: #111827;
            font-size: 1.1rem;
            letter-spacing: -0.25px;
        }
        .chat-list-note {
            color: #6b7280;
            font-size: 0.85rem;
            margin-bottom: 12px;
            font-weight: 400;
        }

        /* 🎨 按鈕樣式 */
        div.stButton > button {
            white-space: pre-wrap;
            height: auto;
            min-height: 44px;
            text-align: center;
            line-height: 1.4;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(123, 91, 163, 0.15);
            font-size: 0.95rem;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(123, 91, 163, 0.25);
        }
        div.stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(123, 91, 163, 0.15);
        }

        /* 📱 主要按鈕 (紫色漸層) */
        [data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #7B5BA3 0%, #9B7BB4 100%);
            color: white;
            box-shadow: 0 4px 16px rgba(123, 91, 163, 0.3);
        }
        [data-testid="baseButton-primary"]:hover {
            background: linear-gradient(135deg, #6a4e8c 0%, #8a6aa3 100%);
            box-shadow: 0 6px 24px rgba(123, 91, 163, 0.4);
        }
        
        /* 改善 expander 樣式 */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #f8f6fc 0%, #f0eaf8 100%);
            border-radius: 12px;
            padding: 16px 20px;
            border: 1px solid rgba(123, 91, 163, 0.2);
            font-weight: 600;
            color: #5A3F7F;
            box-shadow: 0 2px 8px rgba(123, 91, 163, 0.08);
        }
        
        /* 改善 sidebar 樣式 */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f6fc 0%, #f0eaf8 100%);
        }
        
        /* 改善分頁標籤樣式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid rgba(123, 91, 163, 0.1);
            padding-bottom: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 8px;
            border: none;
            padding: 12px 24px;
            font-weight: 600;
            color: #8e8e8e;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(123, 91, 163, 0.1);
            color: #7B5BA3;
            border-color: #7B5BA3;
        }

        /* 📱 次要按鈕 */
        [data-testid="baseButton-secondary"] {
            background: #ffffff;
            color: #7B5BA3;
            border: 2px solid rgba(123, 91, 163, 0.3);
        }
        [data-testid="baseButton-secondary"]:hover {
            background: rgba(123, 91, 163, 0.05);
            border-color: rgba(123, 91, 163, 0.5);
        }
        
        /* 改善容器樣式 */
        [data-testid="stVerticalBlock"] {
            gap: 0;
            border: none;
        }
        [data-testid="stVerticalBlockBorder"] {
            border: none;
        }
        [data-testid="element-container"] {
            border: none;
        }
        
        /* 改善資訊框樣式 */
        .stAlert {
            border-radius: 12px;
            border: 1px solid rgba(123, 91, 163, 0.2);
            box-shadow: 0 4px 12px rgba(123, 91, 163, 0.08);
            font-size: 0.95rem;
            background: linear-gradient(135deg, #f8f6fc 0%, #f0eaf8 100%);
        }
        
        /* 改善圖片樣式 */
        img {
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(123, 91, 163, 0.12);
            margin-bottom: 24px;
            display: block;
        }

        /* ✨ 星星評分 */
        .rating-stars {
            font-size: 1.5rem;
            color: #FFD700;
            margin: 8px 0;
        }

        /* 📊 Info/Success/Warning 盒子 */
        .stAlert {
            border-radius: 12px;
            padding: 16px;
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
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #7B5BA3;'>SwapIt</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem;'>校園以物易物媒合平台</p>", unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(["🔐 登入", "✍️ 建立帳號"])
    
    with login_tab:
        st.markdown("### 歡迎回來")
        account_name = st.text_input("帳號名稱", placeholder="輸入你的帳號")
        password = st.text_input("密碼", type="password", placeholder="輸入密碼")
        if st.button("登入", type="primary", use_container_width=True):
            user = login_user(db(), account_name, password)
            if user:
                st.session_state.user_id = user.user_id
                st.rerun()
            st.error("帳號或密碼不正確。")

    with register_tab:
        st.markdown("### 加入 SwapIt 社群")
        new_account = st.text_input("帳號名稱（全英，可含數字或底線）", placeholder="例如：user123")
        new_password = st.text_input("密碼", type="password", placeholder="至少 6 個字元")
        confirm_password = st.text_input("確認密碼", type="password", placeholder="再輸入一次密碼")
        nickname = st.text_input("暱稱（其他使用者看到的名字）", placeholder="例如：小明")
        full_name = st.text_input("正式姓名（選填）", placeholder="例如：王大明")
        if st.button("建立帳號", type="primary", use_container_width=True):
            try:
                user = register_user(db(), new_account, new_password, confirm_password, nickname, full_name)
                st.session_state.user_id = user.user_id
                st.rerun()
            except ValueError as exc:
                st.error(f"{str(exc)}")



def sidebar(user: User) -> str:
    incoming_count, rejected_count = notification_counts(db(), user.user_id)
    
    st.sidebar.markdown("<h1 style='color: #7B5BA3; text-align: center; font-size: 2.5rem; font-weight: 800; margin: 0 0 1rem 0;'>SwapIt</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    st.sidebar.markdown(f"<p style='color: #7B5BA3; font-weight: 600;'>{user.name}</p>", unsafe_allow_html=True)
    st.sidebar.caption(f"帳號：{display_account(user)}")
    
    # 評分卡片
    st.sidebar.markdown(f"""
    <div class='swap-card' style='text-align: center;'>
    <p style='color: #7B5BA3; font-weight: 600; margin: 0;'>{user.rating:.1f} / 5</p>
    <p style='color: #7B5BA3; font-size: 0.85rem; margin: 5px 0 0 0;'>已完成 {user.completed_trades} 次交換</p>
    </div>
    """, unsafe_allow_html=True)
    
    if incoming_count or rejected_count:
        st.sidebar.warning(f"{incoming_count} 個待回覆，{rejected_count} 個被拒絕", icon="⚠️")

    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #7B5BA3; font-weight: 600;'>目前位置</p>", unsafe_allow_html=True)
    
    browser_location_button()
    default_location = st.session_state.get("current_location_name", "臺南市")
    manual_location = st.sidebar.selectbox(
        "選擇縣市",
        list(TAIWAN_LOCATIONS.keys()),
        index=list(TAIWAN_LOCATIONS.keys()).index(default_location) if default_location in TAIWAN_LOCATIONS else 4,
    )
    if st.sidebar.button("套用位置", use_container_width=True):
        latitude, longitude = location_coords(manual_location)
        save_current_location(manual_location, latitude, longitude)
        st.sidebar.success(f"位置已設定為 {manual_location}")

    current_name = st.session_state.get("current_location_name", "尚未設定")
    st.sidebar.caption(f"推薦會優先顯示靠近「{current_name}」的物品。")

    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='color: #7B5BA3; font-weight: 600;'>功能選單</p>", unsafe_allow_html=True)
    page = st.sidebar.radio(
        "選擇功能",
        ["瀏覽物品", "我的物品", "交換請求與聊天", "歷史交易", "個人資料"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("登出", use_container_width=True):
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


def save_uploaded_image(uploaded_file, prefix: str) -> str:
    if not uploaded_file:
        return ""
    data = uploaded_file.read()
    # Convert to base64 data URL
    base64_data = base64.b64encode(data).decode()
    # Detect mime type from file extension
    filename = os.path.basename(uploaded_file.name)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    return f"data:{mime_type};base64,{base64_data}"


def is_image_path(source: str) -> bool:
    lower = str(source).lower()
    return any(lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]) or lower.startswith("data:image")


def item_card(item: Item, score: float | None = None, score_label: str = "推薦分數", show_actions: bool = False, user: User | None = None) -> None:
    score_line = f"<div class='muted'>{escape(score_label)}：{score:.1f} · {distance_text(item)}</div>" if score is not None else ""
    image_source = item.image_url if item.image_url else None
    
    # 星星評分
    stars = "⭐" * int(item.owner.rating)

    st.markdown('<div class="swap-card">', unsafe_allow_html=True)
    
    # Show inline actions if requested
    if show_actions and user and item.owner_id == user.user_id and item.status == "active":
        col_name, col_actions = st.columns([5, 1])
        with col_name:
            st.markdown(
                f"<h3 style='color: #5A3F7F; font-size: 1.1rem; font-weight: 600; margin: 0 0 12px 0;'>{escape(item.name)}</h3>",
                unsafe_allow_html=True,
            )
        with col_actions:
            c_edit, c_delete = st.columns(2)
            with c_edit:
                if st.button("編輯", key=f"edit_inline_{item.item_id}", help="編輯"):
                    st.session_state.edit_item_id = item.item_id
                    st.rerun()
            with c_delete:
                if st.button("刪除", key=f"delete_inline_{item.item_id}", help="刪除"):
                    try:
                        delete_item(db(), user.user_id, item.item_id)
                        st.success("物品已刪除！")
                        st.rerun()
                    except ValueError as exc:
                        st.error(f"{str(exc)}")
    else:
        st.markdown(
            f"<h3 style='color: #5A3F7F; font-size: 1.1rem; font-weight: 600; margin: 0 0 12px 0;'>{escape(item.name)}</h3>",
            unsafe_allow_html=True,
        )
    
    st.markdown(
        "\n".join(
            [
                f"<div class='muted' style='margin-bottom: 8px;'>{escape(category_label(item.category))} · {escape(item.location or '縣市未設定')} · <span style='color: #7B5BA3; font-weight: 600;'>{escape(STATUS_TEXT.get(item.status, item.status))}</span></div>",
                f"<div class='muted' style='margin-bottom: 20px;'>{score_line}</div>",
            ]
        ),
        unsafe_allow_html=True,
    )
    
    # Only show image if it exists and is valid - in a separate section
    if image_source and is_image_path(image_source):
        st.markdown("<div style='margin: 32px 0; padding: 20px;'>", unsafe_allow_html=True)
        try:
            if image_source.startswith("data:image"):
                st.image(image_source, use_container_width=True)
            elif os.path.exists(image_source):
                st.image(image_source, use_container_width=True)
            elif image_source.startswith("http"):
                st.image(image_source, use_container_width=True)
        except Exception:
            # If image fails to load, just skip it without showing placeholder
            pass
        st.markdown("</div>", unsafe_allow_html=True)
    
    # No placeholder shown even when there's no image
    st.markdown(
        f"<p style='color: #2C2C2C; line-height: 1.6; margin-bottom: 32px;'>{escape(item.description or '尚未填寫描述。')}</p>",
        unsafe_allow_html=True,
    )
    
    with st.container():
        st.markdown(
            f"<div style='display: flex; justify-content: space-between; align-items: center; padding-top: 20px; border-top: 1px solid #E8DDF5; margin-top: 20px;'>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(
                f"<div style='color: #888; font-size: 0.9rem;'><strong style='color: #5A3F7F;'>{escape(item.owner.name)}</strong></div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div style='color: #FFD700; font-size: 1.1rem;'>{stars}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def offer_request_actions(user: User, target_item: Item, key_prefix: str) -> None:
    my_items = active_user_items(db(), user.user_id)
    if not my_items:
        st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
        st.info("你需要先在「我的物品」刊登至少一個交換中的物品，才能送出交換請求。")
        return

    st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
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
                st.error(f"{str(exc)}")


def browse_page(user: User) -> None:
    st.markdown("<h1 style='color: #7B5BA3;'>瀏覽物品</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6b7280; font-size: 0.95rem;'>找到喜歡的物品？用你的物品送出交換請求吧！</p>", unsafe_allow_html=True)
    latitude, longitude = current_coords()

    st.markdown("<h3 style='color: #5A3F7F; font-size: 1.5rem; font-weight: 600;'>搜尋物品</h3>", unsafe_allow_html=True)
    query = st.text_input("搜尋", placeholder="例如：桌燈、電子產品、臺南市、陳小明")
    if query.strip():
        results = search_items(db(), user.user_id, query, limit=20, current_latitude=latitude, current_longitude=longitude)
        if not results:
            st.info("沒有找到符合的物品，可以換個關鍵字試試。")
            return
        st.success(f"找到 {len(results)} 筆結果，已依符合程度與距離排序。")
        for index, (item, score) in enumerate(results, start=1):
            st.markdown(f"<h4 style='color: #5A3F7F; font-size: 1rem; font-weight: 600;'>搜尋結果 {index}</h4>", unsafe_allow_html=True)
            item_card(item, score, score_label="排序分數")
            offer_request_actions(user, item, key_prefix=f"search_{index}")
        return

    st.markdown("<h3 style='color: #5A3F7F; font-size: 1.5rem; font-weight: 600; margin-bottom: 0;'>推薦給你</h3>", unsafe_allow_html=True)
    recommendations = get_recommendations(db(), user.user_id, limit=1, current_latitude=latitude, current_longitude=longitude)
    if not recommendations:
        st.info("目前沒有新的推薦。你可以新增物品、換一個位置，或查看已送出的交換請求。")
        return

    item, score = recommendations[0]
    item_card(item, score)
    offer_request_actions(user, item, key_prefix="recommendation")


def my_items_page(user: User) -> None:
    st.markdown("<h1 style='color: #7B5BA3;'>我的物品</h1>", unsafe_allow_html=True)
    
    # 搜尋功能 - 放在最上方
    st.markdown("<h4 style='color: #5A3F7F; font-size: 1rem; font-weight: 600;'>搜尋你的物品</h4>", unsafe_allow_html=True)
    search_query = st.text_input("輸入物品名稱或描述...", placeholder="例如：水壺、二手...", key="my_items_search")
    
    with st.expander("新增物品", expanded=False):
        st.markdown("<h4 style='color: #5A3F7F; font-size: 1rem; font-weight: 600;'>刊登新物品</h4>", unsafe_allow_html=True)
        categories = category_options()
        name = st.text_input("物品名稱", placeholder="例如：二手桌燈")
        category = st.selectbox("分類", list(categories.keys()), format_func=lambda code: categories[code])
        description = st.text_area("物品描述", height=90, placeholder="描述物品的狀態、使用時長等...")
        location = st.selectbox("物品所在縣市", list(TAIWAN_LOCATIONS.keys()), index=4)
        st.caption("上傳商品圖片或檔案（手機可直接拍照），或使用圖片網址。")
        uploaded_image = st.file_uploader("上傳商品圖片或檔案", type=None)
        image_url = st.text_input("圖片網址（可不填）", placeholder="例如：https://...")
        if st.button("刊登物品", type="primary", use_container_width=True):
            try:
                image_path = ""
                if uploaded_image is not None:
                    image_path = save_uploaded_image(uploaded_image, "item")
                elif image_url:
                    image_path = image_url.strip()
                latitude, longitude = location_coords(location)
                create_item(db(), user.user_id, name, category, description, location, [], image_path, latitude, longitude)
                st.success("物品已成功刊登！")
            except ValueError as exc:
                st.error(f"{str(exc)}")

    st.markdown("<h3 style='color: #5A3F7F; font-size: 1.1rem; font-weight: 600;'>你的物品列表</h3>", unsafe_allow_html=True)
    if "edit_item_id" not in st.session_state:
        st.session_state.edit_item_id = None

    items = db().query(Item).filter(Item.owner_id == user.user_id).order_by(Item.created_at.desc()).all()
    
    # 過濾物品
    if search_query.strip():
        search_lower = search_query.lower()
        items = [item for item in items if 
                  search_lower in item.name.lower() or 
                  (item.description and search_lower in item.description.lower())]
    
    if not items:
        if search_query.strip():
            st.info("沒有找到符合搜尋的物品。")
        else:
            st.info("你還沒有刊登任何物品。")
        return
    
    for item in items:
        item_card(item, show_actions=True, user=user)

    if st.session_state.edit_item_id:
        edit_item = db().get(Item, st.session_state.edit_item_id)
        if not edit_item or edit_item.owner_id != user.user_id or edit_item.status != "active":
            st.warning("無法編輯此物品，請重新選擇一個可編輯的物品。")
            st.session_state.edit_item_id = None
            if st.button("重新整理"): 
                st.rerun()
            return

        st.markdown("<h3 style='color: #5A3F7F; font-size: 1.1rem; font-weight: 600;'>編輯物品</h3>", unsafe_allow_html=True)
        with st.form("edit_item_form"):
            name = st.text_input("物品名稱", value=edit_item.name, placeholder="例如：二手桌燈")
            category = st.selectbox("分類", list(category_options().keys()), index=list(category_options().keys()).index(edit_item.category), format_func=lambda code: category_options()[code])
            description = st.text_area("物品描述", value=edit_item.description or "", height=90, placeholder="描述物品的狀態、使用時長等...")
            location = st.selectbox("物品所在縣市", list(TAIWAN_LOCATIONS.keys()), index=list(TAIWAN_LOCATIONS.keys()).index(edit_item.location or list(TAIWAN_LOCATIONS.keys())[0]))
            st.caption("替換物品圖片或檔案（手機可直接拍照），或使用圖片網址。")
            uploaded_image = st.file_uploader("替換商品圖片或檔案", type=None)
            image_url = st.text_input("圖片網址（填寫則會覆蓋現有圖片）", placeholder="例如：https://...")
            if st.form_submit_button("儲存修改", use_container_width=True):
                try:
                    image_path = edit_item.image_url or ""
                    if uploaded_image is not None:
                        image_path = save_uploaded_image(uploaded_image, "item")
                    elif image_url:
                        image_path = image_url.strip()
                    latitude, longitude = location_coords(location)
                    update_item(db(), user.user_id, edit_item.item_id, name, category, description, location, image_path, latitude, longitude)
                    st.success("物品已更新！")
                    st.session_state.edit_item_id = None
                    st.rerun()
                except ValueError as exc:
                    st.error(f"{str(exc)}")

        if st.button("取消編輯", use_container_width=True, key="cancel_edit_item"):
            st.session_state.edit_item_id = None
            st.rerun()


def trade_request_card(request: TradeRequest, viewer_id: int) -> None:
    is_receiver = request.receiver_id == viewer_id
    if is_receiver:
        title = "收到的交換請求"
        description = f"對方想用「{request.offer_item.name}」交換你的「{request.target_item.name}」"
    else:
        title = "你送出的交換請求"
        description = f"你想用「{request.offer_item.name}」交換對方的「{request.target_item.name}」"

    status_text = REQUEST_STATUS_TEXT.get(request.status, request.status)
    status_colors = {
        "pending": "#FFD700",
        "accepted": "#7CB342",
        "rejected": "#E53935",
        "cancelled": "#757575",
    }
    status_color = status_colors.get(request.status, "#999")

    st.markdown(
        f"""
        <div class='request-box'>
        <h4 style='color: #7B5BA3; margin: 0;'>{escape(title)}</h4>
        <p style='color: #2C2C2C; margin: 10px 0;'>{escape(description)}</p>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <span style='color: {status_color}; font-weight: 600;'>{escape(status_text)}</span>
            <span style='color: #888; font-size: 0.85rem;'>{request.created_at.strftime('%m-%d %H:%M')}</span>
        </div>
        {f"<p style='color: #666; margin: 10px 0 0 0; font-style: italic;'>{escape(request.message)}</p>" if request.message else ""}
        </div>
        """,
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
    
    st.markdown(f"<p style='color: #888;'>收到 <strong style='color: #FF69B4;'>{len(requests)}</strong> 個新請求</p>", unsafe_allow_html=True)
    for request in requests:
        trade_request_card(request, user.user_id)
        left, right = st.columns(2)
        with left:
            if st.button("接受，進入聊天", type="primary", use_container_width=True, key=f"accept_{request.request_id}"):
                try:
                    accept_trade_request(db(), request.request_id, user.user_id)
                    st.success("已接受交換請求，聊天室已建立！")
                    st.rerun()
                except ValueError as exc:
                    st.error(f"{str(exc)}")
        with right:
            if st.button("不接受", use_container_width=True, key=f"reject_{request.request_id}"):
                try:
                    reject_trade_request(db(), request.request_id, user.user_id)
                    st.success("已拒絕交換請求。")
                    st.rerun()
                except ValueError as exc:
                    st.error(f"{str(exc)}")


def outgoing_requests_view(user: User) -> None:
    requests = outgoing_trade_requests(db(), user.user_id)
    if not requests:
        st.info("你還沒有送出任何交換請求。")
        return
    
    st.markdown(f"<p style='color: #888;'>已送出 <strong style='color: #7B5BA3;'>{len(requests)}</strong> 個請求</p>", unsafe_allow_html=True)
    for request in requests:
        trade_request_card(request, user.user_id)
        if request.status == "accepted":
            st.success("對方已接受！請到「聊天室」分頁聯絡對方。")
        elif request.status == "rejected":
            st.warning("對方拒絕了這個交換請求。", icon="😞")


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

    list_col, chat_col = st.columns([1.2, 2.3], gap="medium")
    
    with list_col:
        st.markdown("<h4 style='color: #262626; margin: 0;'>聊天室列表</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8e8e8e; font-size: 0.85rem;'>點選開始對話</p>", unsafe_allow_html=True)
        
        for match_option in matches:
            label = chat_list_label(match_option, user.user_id)
            other = db().get(User, match_option.other_user_id(user.user_id))
            
            # 聊天列表項
            is_selected = match_option.match_id == selected_id
            bg_color = "#fafafa" if is_selected else "#ffffff"
            border_color = "#262626" if is_selected else "#dbdbdb"
            
            if st.button(
                f"{other.name}\n{match_option.item_a.name if match_option.item_a.owner_id == user.user_id else match_option.item_b.name} ↔ {match_option.item_b.name if match_option.item_a.owner_id == user.user_id else match_option.item_a.name}",
                use_container_width=True,
                key=f"chat_pick_{match_option.match_id}",
            ):
                st.session_state.selected_chat_match_id = match_option.match_id
                st.rerun()

    with chat_col:
        match = db().get(Match, st.session_state.selected_chat_match_id)
        other = db().get(User, match.other_user_id(user.user_id))
        mine, theirs = match_items_for_user(match, user.user_id)
        
        st.markdown(f"<h3 style='color: #262626;'>與 {other.name} 的對話</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #8e8e8e; font-size: 0.85rem;'>{mine.name} ↔ {theirs.name}</p>", unsafe_allow_html=True)

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
            status_badge = {
                "active": "進行中",
                "completed": "已完成",
                "cancelled": "已取消",
            }.get(match.status, match.status)
            st.markdown(f"<div style='padding: 8px; background: #fafafa; border-radius: 0; text-align: center; color: #262626; font-weight: 600;'>{status_badge}</div>", unsafe_allow_html=True)

        st.divider()
        
        # 聊天氣泡
        room = match.chat_room
        if room and room.messages:
            for message in room.messages:
                sender = "你" if message.sender_id == user.user_id else message.sender.name
                is_own_message = message.sender_id == user.user_id
                
                if is_own_message:
                    col1, col2 = st.columns([1, 3])
                    with col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #7B5BA3 0%, #5A3F7F 100%); color: white; padding: 12px 16px; border-radius: 14px; margin-bottom: 8px;'>
                        <p style='margin: 0; font-weight: 500;'>{escape(sender)}</p>
                        <p style='margin: 8px 0 4px 0;'>{escape(message.content)}</p>
                        <p style='margin: 0; font-size: 0.8rem; opacity: 0.8;'>{message.created_at.strftime('%H:%M')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style='background: #F5F3FA; color: #2C2C2C; padding: 12px 16px; border-radius: 14px; margin-bottom: 8px; border-left: 3px solid #7B5BA3;'>
                        <p style='margin: 0; font-weight: 500;'>{escape(sender)}</p>
                        <p style='margin: 8px 0 4px 0;'>{escape(message.content)}</p>
                        <p style='margin: 0; font-size: 0.8rem; color: #888;'>{message.created_at.strftime('%H:%M')}</p>
                        </div>
                        """, unsafe_allow_html=True)

        if match.status == "active":
            st.divider()
            content = st.chat_input("輸入訊息...")
            if content:
                send_message(db(), match.match_id, user.user_id, content)
                st.rerun()

        if match.status == "completed":
            st.divider()
            st.markdown("<h4 style='color: #262626;'>評價這次交換</h4>", unsafe_allow_html=True)
            already_reviewed = db().query(Review).filter(Review.match_id == match.match_id, Review.reviewer_id == user.user_id).first()
            if already_reviewed:
                st.success(f"你給了 {already_reviewed.rating} 分，留言：{already_reviewed.comment or '(無)'}")
            else:
                rating = st.slider("評分", 1, 5, 5, label_visibility="collapsed")
                comment = st.text_area("留言", height=80, placeholder="分享這次交換的體驗...")
                if st.button("送出評價", type="primary", use_container_width=True):
                    try:
                        review_match(db(), match.match_id, user.user_id, rating, comment)
                        st.success("評價已送出！")
                        st.rerun()
                    except ValueError as exc:
                        st.error(f"{str(exc)}")


def requests_and_chat_page(user: User) -> None:
    st.markdown("<h1 style='color: #7B5BA3;'>交換請求與聊天</h1>", unsafe_allow_html=True)
    incoming_count, rejected_count = notification_counts(db(), user.user_id)
    st.markdown(f"<p style='color: #6b7280;'>收到待回覆：<strong style='color: #FF69B4;'>{incoming_count}</strong> · 被拒絕通知：<strong style='color: #FF6B9D;'>{rejected_count}</strong></p>", unsafe_allow_html=True)
    
    incoming_tab, outgoing_tab, chat_tab = st.tabs(["收到的請求", "我的請求通知", "聊天室"])
    with incoming_tab:
        incoming_requests_view(user)
    with outgoing_tab:
        outgoing_requests_view(user)
    with chat_tab:
        chat_view(user)


def profile_page(user: User) -> None:
    st.markdown("<h1 style='color: #7B5BA3;'>個人資料</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='swap-card' style='text-align: center;'>
        <p style='color: #262626; font-size: 1.5rem; margin: 0; font-weight: 600;'>{user.rating:.1f}</p>
        <p style='color: #8e8e8e; font-weight: 500; margin: 8px 0 0 0;'>/ 5</p>
        <p style='color: #8e8e8e; font-size: 0.85rem; margin: 4px 0 0 0;'>評分</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='swap-card' style='text-align: center;'>
        <p style='color: #262626; font-size: 1.5rem; margin: 0; font-weight: 600;'>{user.completed_trades}</p>
        <p style='color: #8e8e8e; font-weight: 500; margin: 8px 0 0 0;'>次</p>
        <p style='color: #8e8e8e; font-size: 0.85rem; margin: 4px 0 0 0;'>已完成交換</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='swap-card' style='text-align: center;'>
        <p style='color: #262626; font-size: 1.5rem; margin: 0; font-weight: 600;'>{len(user.items)}</p>
        <p style='color: #8e8e8e; font-weight: 500; margin: 8px 0 0 0;'>個</p>
        <p style='color: #8e8e8e; font-size: 0.85rem; margin: 4px 0 0 0;'>刊登物品</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown(f"<h3 style='color: #262626;'>帳號資訊</h3>", unsafe_allow_html=True)
    st.markdown(f"<p><strong style='color: #262626;'>帳號名稱：</strong> {display_account(user)}</p>", unsafe_allow_html=True)
    if user.full_name:
        st.markdown(f"<p><strong style='color: #262626;'>正式姓名：</strong> {escape(user.full_name)}</p>", unsafe_allow_html=True)

    st.caption("上傳頭像圖片或檔案（手機可直接拍照），或使用網址。")
    uploaded_avatar = st.file_uploader("上傳頭像圖片或檔案", type=None)
    avatar_url = st.text_input("頭像網址（選填）", value=user.avatar_url or "", placeholder="例如：https://...jpg")

    with st.form("edit_profile_form"):
        nickname = st.text_input("暱稱／顯示名稱", value=user.name, max_chars=100)
        formal_name = st.text_input("正式姓名", value=user.full_name or "", max_chars=100)
        dorm = st.text_input("宿舍（縣市或校區）", value=user.dorm or "", max_chars=80)
        bio = st.text_area("個人簡介", value=user.bio or "", height=120, max_chars=500, placeholder="介紹你自己，讓其他人更了解你...")
        submitted = st.form_submit_button("儲存個人資料", use_container_width=True)

        if submitted:
            try:
                avatar_path = user.avatar_url or ""
                if uploaded_avatar is not None:
                    avatar_path = save_uploaded_image(uploaded_avatar, "avatar")
                elif avatar_url:
                    avatar_path = avatar_url.strip()
                update_user_profile(db(), user.user_id, nickname, formal_name, dorm, bio, avatar_path)
                st.success("個人資料已更新！")
            except ValueError as exc:
                st.error(f"{str(exc)}")

    if user.bio:
        st.markdown(f"<div class='swap-card'><p style='color: #666; font-style: italic;'>{escape(user.bio)}</p></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color: #888; font-style: italic;'>尚未填寫自我介紹。</p>", unsafe_allow_html=True)

    if user.dorm:
        st.markdown(f"<p><strong style='color: #262626;'>宿舍／位置：</strong> {escape(user.dorm)}</p>", unsafe_allow_html=True)
    if user.avatar_url:
        st.image(user.avatar_url, width=120)


def history_page(user: User) -> None:
    st.markdown("<h1 style='color: #7B5BA3;'>歷史交易</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6b7280;'>查看所有已完成和已取消的交易紀錄。</p>", unsafe_allow_html=True)
    
    history_matches = user_history_matches(db(), user.user_id)
    if not history_matches:
        st.info("目前沒有歷史交易紀錄。")
        return
    
    # 分別篩選已完成和已取消的交易
    completed_matches = [m for m in history_matches if m.status == "completed"]
    cancelled_matches = [m for m in history_matches if m.status == "cancelled"]
    
    # 已完成的交易
    if completed_matches:
        st.markdown("<h2 style='color: #5A3F7F;'>已完成的交易</h2>", unsafe_allow_html=True)
        for match in completed_matches:
            mine, theirs = match_items_for_user(match, user.user_id)
            other = db().get(User, match.other_user_id(user.user_id))
            user_review = get_user_review(db(), match.match_id, user.user_id)
            other_review = get_user_review(db(), match.match_id, match.other_user_id(user.user_id))
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"<h4 style='color: #5A3F7F; margin: 0;'>{escape(mine.name)} ↔ {escape(theirs.name)}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #6b7280; margin: 8px 0;'>{escape(other.name)} · {other.rating:.1f}</p>", unsafe_allow_html=True)
                    st.caption(f"完成時間：{match.completed_at.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if user_review:
                        st.markdown(f"<div style='text-align: center; padding: 10px; background: #fafafa; border-radius: 0;'><strong style='color: #262626; font-size: 1.2rem;'>{user_review.rating}</strong><br><small style='color: #8e8e8e;'>分</small></div>", unsafe_allow_html=True)
                    else:
                        st.info("尚未評分")
                
                # 評分按鈕
                if not user_review:
                    st.divider()
                    rating_col, comment_col = st.columns([1, 2])
                    with rating_col:
                        rating = st.slider(
                            "評分",
                            1, 5, 5,
                            key=f"history_rating_{match.match_id}",
                            label_visibility="collapsed"
                        )
                    with comment_col:
                        comment = st.text_input(
                            "評論",
                            key=f"history_comment_{match.match_id}",
                            placeholder="分享你的評論...",
                            label_visibility="collapsed"
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
                            st.error(f"{str(exc)}")
                else:
                    if user_review.comment:
                        st.markdown(f"<p style='color: #666; font-style: italic;'>{escape(user_review.comment)}</p>", unsafe_allow_html=True)
    
    # 已取消的交易
    if cancelled_matches:
        st.markdown("<h2 style='color: #5A3F7F;'>已取消的交易</h2>", unsafe_allow_html=True)
        for match in cancelled_matches:
            mine, theirs = match_items_for_user(match, user.user_id)
            other = db().get(User, match.other_user_id(user.user_id))
            
            with st.container(border=True):
                st.markdown(f"<h4 style='color: #5A3F7F;'>{escape(mine.name)} ↔ {escape(theirs.name)}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #6b7280;'>{escape(other.name)}</p>", unsafe_allow_html=True)
                st.caption(f"取消時間：{match.updated_at.strftime('%Y-%m-%d %H:%M')}")


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
