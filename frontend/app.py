import streamlit as st
import requests
import uuid
import base64
from datetime import datetime

API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="智能服装穿搭助手",
    page_icon="👗",
    layout="wide"
)


def check_backend():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def api_register(username: str, password: str, email: str = None):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            json={"username": username, "password": password, "email": email},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            return {"error": response.json().get("detail", "注册失败")}
        return {"error": "注册失败"}
    except Exception as e:
        return {"error": str(e)}


def api_login(username: str, password: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"error": "用户名或密码错误"}
        return {"error": "登录失败"}
    except Exception as e:
        return {"error": str(e)}


def api_get_user(user_id: str):
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/user/{user_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def api_update_profile(user_id: str, profile: dict):
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/auth/profile/{user_id}",
            json=profile,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def send_message(message: str, user_id: str, session_id: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json={"message": message, "user_id": user_id, "session_id": session_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None


def search_by_image(image_url: str, user_id: str, session_id: str = None):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat/image-search",
            json={"image_url": image_url, "user_id": user_id, "session_id": session_id},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None


def send_message_with_image(message: str, user_id: str, session_id: str, image_url: str = None):
    try:
        payload = {"message": message, "user_id": user_id, "session_id": session_id}
        if image_url:
            payload["image_url"] = image_url
        
        response = requests.post(
            f"{API_BASE_URL}/api/chat/",
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None


def get_user_outfits(user_id: str):
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/wardrobe/list/{user_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def delete_outfit(outfit_id: str):
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/wardrobe/{outfit_id}",
            timeout=10
        )
        return response.status_code == 200
    except:
        return False


def toggle_favorite(outfit_id: str):
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/wardrobe/{outfit_id}/favorite",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def save_outfit(name: str, items: list, user_id: str, style: str = None, occasion: str = None, is_favorite: bool = True):
    try:
        outfit_data = {
            "user_id": user_id,
            "name": name,
            "style": style,
            "occasion": occasion,
            "items": items,
            "outfit_image": None,
            "is_favorite": is_favorite
        }
        response = requests.post(
            f"{API_BASE_URL}/api/wardrobe/save-outfit",
            json=outfit_data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def init_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'is_logged_in' not in st.session_state:
        st.session_state.is_logged_in = False
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'messages' not in st.session_state:
        st.session_state.messages = []


init_session_state()


def show_login_page():
    st.title("👗 智能服装穿搭助手")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 登录", "📝 注册"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=True):
            st.subheader("用户登录")
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                submitted = st.form_submit_button("登录", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.warning("请输入用户名和密码")
                else:
                    result = api_login(username, password)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.user_id = result["id"]
                        st.session_state.user_info = result
                        st.session_state.is_logged_in = True
                        st.session_state.session_id = str(uuid.uuid4())
                        st.session_state.messages = []
                        st.rerun()
    
    with tab2:
        with st.form("register_form", clear_on_submit=True):
            st.subheader("新用户注册")
            new_username = st.text_input("用户名", placeholder="请输入用户名")
            new_password = st.text_input("密码", type="password", placeholder="请输入密码")
            confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
            email = st.text_input("邮箱（选填）", placeholder="请输入邮箱")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                submitted = st.form_submit_button("注册", use_container_width=True)
            
            if submitted:
                if not new_username or not new_password:
                    st.warning("请输入用户名和密码")
                elif new_password != confirm_password:
                    st.error("两次输入的密码不一致")
                elif len(new_password) < 6:
                    st.warning("密码长度至少6位")
                else:
                    result = api_register(new_username, new_password, email or None)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("注册成功！请登录")
                        st.rerun()
    
    st.markdown("---")
    st.markdown("##### 💡 提示：注册后首次登录需要填写您的体型信息，以便我们为您提供更精准的穿搭推荐。")


def show_body_info_page():
    st.title("📋 完善体型信息")
    st.markdown("为了给您提供更精准的穿搭推荐，请填写以下信息：")
    st.markdown("---")
    
    profile = st.session_state.user_info.get("profile") or {}
    
    with st.form("body_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox(
                "性别",
                ["", "男", "女", "其他"],
                index=["", "男", "女", "其他"].index(profile.get("gender", "")) if profile.get("gender", "") in ["", "男", "女", "其他"] else 0
            )
            age = st.number_input(
                "年龄",
                min_value=10,
                max_value=100,
                value=profile.get("age", 25)
            )
            height = st.number_input(
                "身高 (cm)",
                min_value=100,
                max_value=250,
                value=int(profile.get("height", 170))
            )
        
        with col2:
            weight = st.number_input(
                "体重 (kg)",
                min_value=30,
                max_value=200,
                value=int(profile.get("weight", 65))
            )
            body_type = st.selectbox(
                "身材类型",
                ["", "梨型", "苹果型", "沙漏型", "H型"],
                index=["", "梨型", "苹果型", "沙漏型", "H型"].index(profile.get("body_type", "")) if profile.get("body_type", "") in ["", "梨型", "苹果型", "沙漏型", "H型"] else 0
            )
        
        st.markdown("##### 📌 身材类型说明")
        st.markdown("""
        - **梨型**: 肩窄臀宽，下身偏胖
        - **苹果型**: 肩宽臀窄，上身偏胖
        - **沙漏型**: 肩臀宽度相近，腰部纤细
        - **H型**: 肩臀宽度相近，腰线不明显
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submitted = st.form_submit_button("保存并进入", use_container_width=True)
        
        if submitted:
            if not gender:
                st.warning("请选择性别")
            elif not body_type:
                st.warning("请选择身材类型")
            else:
                profile_data = {
                    "gender": gender,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "body_type": body_type
                }
                result = api_update_profile(st.session_state.user_id, profile_data)
                if result:
                    st.session_state.user_info = result
                    st.success("信息已保存！")
                    st.rerun()
                else:
                    st.error("保存失败，请重试")


def show_main_app():
    backend_online = check_backend()
    if not backend_online:
        st.warning("⚠️ 后端服务未连接，请确保 FastAPI 服务正在运行")
        return
    
    user_info = st.session_state.user_info
    profile_complete = user_info.get("is_profile_complete", False) if user_info else False
    
    st.title(f"👗 智能服装穿搭助手 | 欢迎，{user_info.get('username', '用户')}")
    
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("退出登录", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    if not profile_complete:
        st.info("📋 请完善您的体型信息，以获得更精准的穿搭推荐")
        if st.button("立即完善体型信息"):
            st.session_state.show_profile_setup = True
    
    st.markdown("---")
    
    page = st.sidebar.radio(
        "功能菜单",
        ["💬 AI对话", "👔 虚拟衣橱", "👤 个人信息"],
        index=0
    )
    
    if page == "💬 AI对话":
        show_chat_page()
    elif page == "👔 虚拟衣橱":
        show_wardrobe_page()
    elif page == "👤 个人信息":
        show_profile_page()


def show_chat_page():
    st.header("💬 AI穿搭对话")
    
    user_info = st.session_state.user_info
    profile = user_info.get("profile", {}) if user_info else {}
    
    if profile:
        st.info(f"📍 当前用户信息: {profile.get('gender', '')} | {profile.get('age', '')}岁 | {profile.get('height', '')}cm | {profile.get('weight', '')}kg | {profile.get('body_type', '')}身材")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_input(
            "请输入您的需求",
            placeholder="例如: 推荐一套商务休闲搭配",
            key="chat_input"
        )
        image_url_input = st.text_input(
            "📷 可选：输入图片URL（AI会根据图片风格辅助搜索）",
            placeholder="https://example.com/image.jpg",
            key="image_url_input"
        )
        uploaded_file = st.file_uploader(
            "或上传本地图片文件",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="chat_image_uploader"
        )
        if uploaded_file:
            st.image(uploaded_file, caption="已上传图片", width=150)
    
    with col2:
        st.write("")
        st.write("")
        send_button = st.button("发送 ✈️", type="primary")
    
    if send_button and user_input:
        with st.spinner("AI正在为您分析..."):
            image_url = image_url_input if image_url_input else None
            
            if uploaded_file and not image_url_input:
                try:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    if uploaded_file.type == 'image/png':
                        image_url = f"data:image/png;base64,{base64_image}"
                    else:
                        image_url = f"data:image/jpeg;base64,{base64_image}"
                except Exception as e:
                    st.warning(f"图片处理失败: {e}")
            
            result = send_message_with_image(user_input, st.session_state.user_id, st.session_state.session_id, image_url)
            
            if result:
                content_preview = user_input
                if uploaded_file:
                    content_preview = f"{user_input} [附带参考图片]"
                
                st.session_state.messages.append({
                    "role": "user",
                    "content": content_preview,
                    "time": datetime.now(),
                    "image": image_url
                })
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result,
                    "time": datetime.now()
                })
    
    st.divider()
    st.subheader("对话历史")
    
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**您**: {msg['content']}")
        else:
            with st.chat_message("assistant"):
                content = msg["content"]
                if isinstance(content, dict):
                    if content.get("intent") == "recommendation":
                        st.write(f"🤖 {content.get('message', '为您推荐：')}")
                        
                        outfit_name = content.get("outfit_name", "推荐搭配")
                        items = content.get("items", [])
                        outfit_image = content.get("outfit_image")
                        
                        if outfit_image:
                            st.image(outfit_image, width=300)
                        
                        if items:
                            st.write(f"**搭配名称**: {outfit_name}")
                            st.write(f"**包含 {len(items)} 件商品**")
                            
                            cols = st.columns(min(len(items), 3))
                            for idx, item in enumerate(items):
                                with cols[idx % 3]:
                                    if item.get("image_url"):
                                        st.image(item["image_url"], width=150)
                                    st.write(f"**{item.get('name', '商品')}**")
                                    st.write(f"💰 ¥{item.get('price', 0)}")
                                    
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        if st.button("🛒 查看", key=f"view_{msg['time']}_{idx}"):
                                            if item.get("product_url"):
                                                st.markdown(f"[点击查看商品]({item['product_url']})")
                                    with col_b:
                                        if st.button("❤️ 收藏", key=f"save_{msg['time']}_{idx}"):
                                            if not st.session_state.user_id:
                                                st.error("请先登录后再收藏")
                                            else:
                                                formatted_items = []
                                                for item in items:
                                                    formatted_items.append({
                                                        'product_name': item.get('name', ''),
                                                        'product_price': item.get('price', 0),
                                                        'product_image_url': item.get('image_url', ''),
                                                        'product_url': item.get('product_url', '')
                                                    })
                                                saved = save_outfit(
                                                    outfit_name,
                                                    formatted_items,
                                                    st.session_state.user_id,
                                                    style=content.get("filters", {}).get("style")
                                                )
                                                if saved:
                                                    st.success("已收藏到衣橱!")
                                                else:
                                                    st.error("收藏失败")
                    
                    elif content.get("intent") == "search":
                        st.write(f"🔍 搜索结果:")
                        
                        keyword = content.get("keyword", "")
                        items = content.get("items", [])
                        
                        st.write(f"**关键词**: {keyword}")
                        st.write(f"**找到 {len(items)} 件商品**")
                        
                        if items:
                            cols = st.columns(min(len(items), 4))
                            for idx, item in enumerate(items):
                                with cols[idx % 4]:
                                    if item.get("image_url"):
                                        st.image(item["image_url"], width=120)
                                    st.write(f"**{item.get('name', '商品')[:20]}...**")
                                    st.write(f"💰 ¥{item.get('price', 0)}")
                                    if st.button("查看", key=f"search_view_{msg['time']}_{idx}"):
                                        if item.get("product_url"):
                                            st.markdown(f"[点击查看商品]({item['product_url']})")
                    
                    elif content.get("intent") == "image_search":
                        st.write(f"🖼️ 图片搜索结果:")
                        
                        items = content.get("items", [])
                        analysis = content.get("analysis", "")
                        message = content.get("message", "")
                        
                        if analysis:
                            st.write(f"**图片风格分析**: {analysis}")
                        if message:
                            st.write(f"🤖 {message}")
                        
                        filters = content.get("filters", {})
                        if filters:
                            filter_str = " | ".join([f"{k}: {v}" for k, v in filters.items() if v])
                            st.write(f"**识别条件**: {filter_str}")
                        
                        st.write(f"**找到 {len(items)} 件相似商品**")
                        
                        if items:
                            cols = st.columns(min(len(items), 4))
                            for idx, item in enumerate(items):
                                with cols[idx % 4]:
                                    if item.get("image_url"):
                                        st.image(item["image_url"], width=120)
                                    st.write(f"**{item.get('name', '商品')[:20]}...**")
                                    st.write(f"💰 ¥{item.get('price', 0)}")
                                    
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        if st.button("🛒 查看", key=f"img_view_{msg['time']}_{idx}"):
                                            if item.get("product_url"):
                                                st.markdown(f"[点击查看商品]({item['product_url']})")
                                    with col_b:
                                        if st.button("❤️ 收藏", key=f"img_save_{msg['time']}_{idx}"):
                                            if not st.session_state.user_id:
                                                st.error("请先登录后再收藏")
                                            else:
                                                formatted_items = []
                                                for i in items:
                                                    formatted_items.append({
                                                        'product_name': i.get('name', ''),
                                                        'product_price': i.get('price', 0),
                                                        'product_image_url': i.get('image_url', ''),
                                                        'product_url': i.get('product_url', '')
                                                    })
                                                saved = save_outfit(
                                                    filters.get('style', '图片搜索') + '搭配',
                                                    formatted_items,
                                                    st.session_state.user_id,
                                                    style=filters.get('style')
                                                )
                                                if saved:
                                                    st.success("已收藏到衣橱!")
                                                else:
                                                    st.error("收藏失败")
                    
                    else:
                        st.write(f"🤖 {content.get('message', '')}")
                else:
                    st.write(f"🤖 {content}")
    
    if not st.session_state.messages:
        st.info("👆 请在上方输入您的穿搭需求，我会为您推荐合适的搭配或搜索商品！")


def show_wardrobe_page():
    st.header("👔 我的虚拟衣橱")
    
    outfits = get_user_outfits(st.session_state.user_id)
    
    if not outfits:
        st.info("您的衣橱还没有收藏任何搭配，快去 AI对话 页面添加吧！")
    else:
        tabs = st.tabs(["全部搭配", "我的收藏"])
        
        with tabs[0]:
            st.write(f"共 {len(outfits)} 套搭配")
            
            for outfit in outfits:
                with st.expander(f"📦 {outfit.get('name', '未命名搭配')} | {outfit.get('style', '未分类') or '未分类'} | {outfit.get('occasion', '未指定') or '未指定'}", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if outfit.get("outfit_image"):
                            st.image(outfit["outfit_image"], width=150)
                        st.write(f"**风格**: {outfit.get('style', '未分类') or '未分类'}")
                        st.write(f"**场合**: {outfit.get('occasion', '未指定') or '未指定'}")
                        st.write(f"**商品数**: {len(outfit.get('items', []))}")
                        if outfit.get("is_favorite"):
                            st.write("❤️ 已收藏")
                        
                        col_del, col_fav = st.columns(2)
                        with col_del:
                            if st.button("🗑️ 删除", key=f"del_{outfit.get('id')}"):
                                if delete_outfit(outfit.get('id')):
                                    st.success("已删除")
                                    st.rerun()
                                else:
                                    st.error("删除失败")
                        with col_fav:
                            fav_label = "⭐ 取消收藏" if outfit.get("is_favorite") else "❤️ 收藏"
                            if st.button(fav_label, key=f"fav_{outfit.get('id')}"):
                                result = toggle_favorite(outfit.get('id'))
                                if result:
                                    st.rerun()
                    
                    with col2:
                        st.write("**商品列表**:")
                        for item in outfit.get("items", []):
                            col_img, col_info = st.columns([1, 3])
                            with col_img:
                                if item.get("product_image_url"):
                                    st.image(item["product_image_url"], width=80)
                            with col_info:
                                st.write(f"**{item.get('product_name', '商品')[:30]}...**" if len(item.get('product_name', '')) > 30 else f"**{item.get('product_name', '商品')}**")
                                st.write(f"💰 ¥{item.get('product_price', 0)}")
                                if item.get("product_url"):
                                    st.markdown(f"[🔗 查看商品链接]({item.get('product_url')})")
        
        with tabs[1]:
            favorites = [o for o in outfits if o.get("is_favorite")]
            if not favorites:
                st.info("还没有收藏任何搭配，可以点击❤️按钮收藏")
            else:
                st.write(f"共 {len(favorites)} 套收藏搭配")
                
                for outfit in favorites:
                    with st.expander(f"❤️ {outfit.get('name', '未命名搭配')} | {outfit.get('style', '未分类') or '未分类'}", expanded=False):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.write(f"**风格**: {outfit.get('style', '未分类') or '未分类'}")
                            st.write(f"**场合**: {outfit.get('occasion', '未指定') or '未指定'}")
                            st.write(f"**商品数**: {len(outfit.get('items', []))}")
                            if st.button("🗑️ 删除", key=f"fav_del_{outfit.get('id')}"):
                                if delete_outfit(outfit.get('id')):
                                    st.success("已删除")
                                    st.rerun()
                                else:
                                    st.error("删除失败")
                        
                        with col2:
                            for item in outfit.get("items", []):
                                col_img, col_info = st.columns([1, 3])
                                with col_img:
                                    if item.get("product_image_url"):
                                        st.image(item["product_image_url"], width=80)
                                with col_info:
                                    st.write(f"**{item.get('product_name', '商品')[:30]}...**" if len(item.get('product_name', '')) > 30 else f"**{item.get('product_name', '商品')}**")
                                    st.write(f"💰 ¥{item.get('product_price', 0)}")


def show_profile_page():
    st.header("👤 个人信息")
    
    user_info = st.session_state.user_info
    profile = user_info.get("profile", {}) if user_info else {}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("账户信息")
        st.write(f"**用户名**: {user_info.get('username', '-')}")
        st.write(f"**邮箱**: {user_info.get('email', '-')}")
        st.write(f"**注册时间**: {user_info.get('created_at', '-')[:10] if user_info.get('created_at') else '-'}")
    
    with col2:
        st.subheader("体型档案")
        
        with st.form("profile_form", clear_on_submit=False):
            col_a, col_b = st.columns(2)
            
            with col_a:
                gender = st.selectbox(
                    "性别",
                    ["男", "女", "其他"],
                    index=["男", "女", "其他"].index(profile.get("gender", "男")) if profile.get("gender", "男") in ["男", "女", "其他"] else 0
                )
                age = st.number_input(
                    "年龄",
                    min_value=10,
                    max_value=100,
                    value=profile.get("age", 25)
                )
                height = st.number_input(
                    "身高 (cm)",
                    min_value=100,
                    max_value=250,
                    value=int(profile.get("height", 170))
                )
            
            with col_b:
                weight = st.number_input(
                    "体重 (kg)",
                    min_value=30,
                    max_value=200,
                    value=int(profile.get("weight", 65))
                )
                body_type = st.selectbox(
                    "身材类型",
                    ["梨型", "苹果型", "沙漏型", "H型"],
                    index=["梨型", "苹果型", "沙漏型", "H型"].index(profile.get("body_type", "H型")) if profile.get("body_type", "H型") in ["梨型", "苹果型", "沙漏型", "H型"] else 3
                )
            
            submitted = st.form_submit_button("保存修改")
            if submitted:
                profile_data = {
                    "gender": gender,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "body_type": body_type
                }
                result = api_update_profile(st.session_state.user_id, profile_data)
                if result:
                    st.session_state.user_info = result
                    st.success("个人信息已保存！")
                else:
                    st.error("保存失败，请重试")


if __name__ == "__main__":
    if not st.session_state.is_logged_in:
        show_login_page()
    elif not st.session_state.user_info.get("is_profile_complete", False):
        show_body_info_page()
    else:
        show_main_app()
