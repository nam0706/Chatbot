"""
app.py - Giao diện Streamlit cho IT Chatbot
Thân xác của chatbot: dark tech theme, bubble chat, lịch sử hội thoại.
Tích hợp đăng nhập Google OAuth 2.0 và lưu lịch sử vào SQLite.
"""

import streamlit as st
from logic_ai import chat_voi_ai, khoi_tao_lich_su, them_vao_lich_su

# ─── Cấu hình trang ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ITBot - Trợ Lý AI Ngành CNTT",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Imports & Env ───────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv
load_dotenv()

from database import add_message, get_or_create_user, get_display_history, get_user_history
from auth import tao_url_dang_nhap, doi_code_lay_tokens, lay_thong_tin_nguoi_dung, kiem_tra_cau_hinh

# ─── Xử lý OAuth Callback (đọc ?code= từ URL) ────────────────────────────────
params = st.query_params
if "code" in params and not st.session_state.get("logged_in", False):
    code = params["code"]
    with st.spinner("🔐 Đang xác thực tài khoản Google..."):
        tokens = doi_code_lay_tokens(code)
        if tokens and "access_token" in tokens:
            user_info = lay_thong_tin_nguoi_dung(tokens["access_token"])
            if user_info and user_info.get("email"):
                # Lưu/cập nhật user vào DB
                get_or_create_user(
                    email=user_info["email"],
                    name=user_info["name"],
                    avatar_url=user_info["picture"],
                )
                # Lưu vào session
                st.session_state.logged_in = True
                st.session_state.user_email = user_info["email"]
                st.session_state.user_name = user_info["name"]
                st.session_state.user_avatar = user_info["picture"]
                st.session_state.da_tai_lich_su = False  # Chưa tải lịch sử
                # Xóa ?code= khỏi URL để tránh xử lý lại khi refresh
                st.query_params.clear()
                st.rerun()
            else:
                st.error("❌ Không lấy được thông tin tài khoản Google. Vui lòng thử lại.")
                st.query_params.clear()
        else:
            st.error("❌ Xác thực thất bại. Vui lòng thử lại.")
            st.query_params.clear()

# ─── Khởi tạo Session State ──────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.user_avatar = ""

if "da_tai_lich_su" not in st.session_state:
    st.session_state.da_tai_lich_su = False

if "lich_su" not in st.session_state:
    st.session_state.lich_su = khoi_tao_lich_su()

if "hien_thi" not in st.session_state:
    st.session_state.hien_thi = []

if "da_gui" not in st.session_state:
    st.session_state.da_gui = False

# ─── Tải lịch sử từ DB khi vừa đăng nhập ────────────────────────────────────
if st.session_state.logged_in and not st.session_state.da_tai_lich_su:
    email = st.session_state.user_email
    # Lịch sử hiển thị chat UI
    st.session_state.hien_thi = get_display_history(email)
    # Lịch sử Gemini SDK (chỉ role user/model, không có hình ảnh)
    raw_history = get_user_history(email)
    if raw_history:
        st.session_state.lich_su = raw_history
    st.session_state.da_tai_lich_su = True


# ─── CSS Tuỳ chỉnh (Dynamic Theme) ──────────────────────────────────────────
light_css = """
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #F0F4F8 0%, #FFFFFF 50%, #F0F4F8 100%); }
.itbot-header { text-align: center; padding: 1.5rem 0 1rem 0; margin-bottom: 1rem; }
.itbot-header h1 { font-size: 2.2rem; font-weight: 700; background: linear-gradient(90deg, #0056b3, #007BFF, #0056b3); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: shine 3s linear infinite; margin: 0; }
@keyframes shine { to { background-position: 200% center; } }
.itbot-header p { color: #475569; font-size: 0.95rem; margin: 0.3rem 0 0 0; }
.chat-container { display: flex; flex-direction: column; gap: 0.8rem; padding: 0.5rem 0; }
.bubble-user { display: flex; justify-content: flex-end; align-items: flex-end; gap: 0.5rem; animation: slideInRight 0.3s ease; }
.bubble-user .bubble-content { background: linear-gradient(135deg, #007BFF, #0056b3); color: #fff; padding: 0.75rem 1.1rem; border-radius: 18px 18px 4px 18px; max-width: 75%; font-size: 0.95rem; line-height: 1.5; box-shadow: 0 4px 15px rgba(0,123,255,0.2); }
.bubble-ai { display: flex; justify-content: flex-start; align-items: flex-start; gap: 0.5rem; animation: slideInLeft 0.3s ease; }
.bubble-ai .avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #E0F7FA, #B2EBF2); display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; box-shadow: 0 0 12px rgba(0,188,212,0.3); }
.bubble-ai .bubble-content { background: #FFFFFF; color: #1E293B; padding: 0.75rem 1.1rem; border-radius: 18px 18px 18px 4px; max-width: 80%; font-size: 0.95rem; line-height: 1.6; border: 1px solid rgba(0,123,255,0.15); box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
@keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes slideInLeft { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
.stTextInput > div > div > input { background: #FFFFFF !important; border: 1.5px solid rgba(0,123,255,0.3) !important; border-radius: 12px !important; color: #1E293B !important; padding: 0.75rem 1rem !important; font-size: 0.95rem !important; }
.stTextInput > div > div > input:focus { border-color: #007BFF !important; box-shadow: 0 0 0 2px rgba(0,123,255,0.15) !important; }
.stButton > button { background: linear-gradient(135deg, #007BFF, #00BFFF) !important; color: #FFFFFF !important; font-weight: 600 !important; border: none !important; border-radius: 10px !important; padding: 0.5rem 1.5rem !important; transition: all 0.2s ease !important; }
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(0,123,255,0.3) !important; color: #FFFFFF !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important; border-right: 1px solid rgba(0,123,255,0.1) !important; }
.welcome-box { background: linear-gradient(135deg, rgba(0,123,255,0.05), rgba(0,191,255,0.05)); border: 1px solid rgba(0,123,255,0.2); border-radius: 12px; padding: 1rem 1.2rem; margin: 1rem 0; color: #334155; font-size: 0.9rem; line-height: 1.6; }
.custom-divider { border: none; border-top: 1px solid rgba(0,123,255,0.15); margin: 1rem 0; }
.user-card { background: linear-gradient(135deg, rgba(0,123,255,0.05), rgba(0,191,255,0.08)); border: 1px solid rgba(0,123,255,0.2); border-radius: 12px; padding: 0.8rem 1rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 0.7rem; }
.user-card img { width: 40px; height: 40px; border-radius: 50%; border: 2px solid rgba(0,123,255,0.3); }
.user-card .user-info { font-size: 0.85rem; color: #1E293B; }
.user-card .user-info strong { display: block; font-size: 0.9rem; }
.google-btn { display: inline-flex; align-items: center; gap: 0.5rem; background: #FFFFFF; color: #1E293B; border: 1.5px solid #DADCE0; border-radius: 10px; padding: 0.6rem 1.2rem; font-size: 0.9rem; font-weight: 500; cursor: pointer; text-decoration: none; width: 100%; justify-content: center; transition: all 0.2s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.google-btn:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.15); background: #F8FAFC; }
::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #F0F4F8; } ::-webkit-scrollbar-thumb { background: rgba(0,123,255,0.3); border-radius: 3px; }
"""

dark_css = """
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0D1117 50%, #0A0E1A 100%) !important; }
.itbot-header { text-align: center; padding: 1.5rem 0 1rem 0; margin-bottom: 1rem; }
.itbot-header h1 { font-size: 2.2rem; font-weight: 700; background: linear-gradient(90deg, #00D4FF, #7B2FFF, #00D4FF); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: shine 3s linear infinite; margin: 0; }
@keyframes shine { to { background-position: 200% center; } }
.itbot-header p { color: #64748B; font-size: 0.95rem; margin: 0.3rem 0 0 0; }
.chat-container { display: flex; flex-direction: column; gap: 0.8rem; padding: 0.5rem 0; }
.bubble-user { display: flex; justify-content: flex-end; align-items: flex-end; gap: 0.5rem; animation: slideInRight 0.3s ease; }
.bubble-user .bubble-content { background: linear-gradient(135deg, #7B2FFF, #5B21B6); color: #fff; padding: 0.75rem 1.1rem; border-radius: 18px 18px 4px 18px; max-width: 75%; font-size: 0.95rem; line-height: 1.5; box-shadow: 0 4px 15px rgba(123,47,255,0.3); }
.bubble-ai { display: flex; justify-content: flex-start; align-items: flex-start; gap: 0.5rem; animation: slideInLeft 0.3s ease; }
.bubble-ai .avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #00D4FF, #0099BB); display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; box-shadow: 0 0 12px rgba(0,212,255,0.4); }
.bubble-ai .bubble-content { background: linear-gradient(135deg, #111827, #1F2937); color: #E2E8F0; padding: 0.75rem 1.1rem; border-radius: 18px 18px 18px 4px; max-width: 80%; font-size: 0.95rem; line-height: 1.6; border: 1px solid rgba(0,212,255,0.15); box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
@keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes slideInLeft { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
.stTextInput > div > div > input { background: #111827 !important; border: 1.5px solid rgba(0,212,255,0.3) !important; border-radius: 12px !important; color: #E2E8F0 !important; padding: 0.75rem 1rem !important; font-size: 0.95rem !important; }
.stTextInput > div > div > input:focus { border-color: #00D4FF !important; box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important; }
.stButton > button { background: linear-gradient(135deg, #00D4FF, #0099BB) !important; color: #0A0E1A !important; font-weight: 600 !important; border: none !important; border-radius: 10px !important; padding: 0.5rem 1.5rem !important; transition: all 0.2s ease !important; }
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(0,212,255,0.4) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1117 0%, #111827 100%) !important; border-right: 1px solid rgba(0,212,255,0.1) !important; }
.welcome-box { background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,255,0.08)); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 1rem 1.2rem; margin: 1rem 0; color: #94A3B8; font-size: 0.9rem; line-height: 1.6; }
.custom-divider { border: none; border-top: 1px solid rgba(0,212,255,0.15); margin: 1rem 0; }
.user-card { background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,255,0.08)); border: 1px solid rgba(0,212,255,0.2); border-radius: 12px; padding: 0.8rem 1rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 0.7rem; }
.user-card img { width: 40px; height: 40px; border-radius: 50%; border: 2px solid rgba(0,212,255,0.4); }
.user-card .user-info { font-size: 0.85rem; color: #94A3B8; }
.user-card .user-info strong { display: block; font-size: 0.9rem; color: #E2E8F0; }
.google-btn { display: inline-flex; align-items: center; gap: 0.5rem; background: #1F2937; color: #E2E8F0; border: 1.5px solid rgba(0,212,255,0.3); border-radius: 10px; padding: 0.6rem 1.2rem; font-size: 0.9rem; font-weight: 500; cursor: pointer; text-decoration: none; width: 100%; justify-content: center; transition: all 0.2s ease; }
.google-btn:hover { border-color: #00D4FF; box-shadow: 0 0 15px rgba(0,212,255,0.2); }

/* Overwrite streamlit markdown text color globally for dark mode */
.stMarkdown p, .stMarkdown li, h2, h3 { color: #E2E8F0 !important; }
::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: #0A0E1A; } ::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
"""

if st.session_state.theme == "light":
    st.markdown(f"<style>{light_css}</style>", unsafe_allow_html=True)
else:
    st.markdown(f"<style>{dark_css}</style>", unsafe_allow_html=True)



# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # --- Logo ITBot ---
    try:
        from PIL import Image
        logo = Image.open("assets/logo.png")
        st.image(logo, use_container_width=True)
    except Exception:
        st.markdown("## ITBot")
        
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    
    # ─── Google Login Section ────────────────────────────────────────────────
    if st.session_state.logged_in:
        # Hiển thị avatar và thông tin user
        avatar_url = st.session_state.get("user_avatar", "")
        name = st.session_state.get("user_name", "Người dùng")
        email = st.session_state.get("user_email", "")
        
        if avatar_url:
            st.markdown(f"""
<div class="user-card">
    <img src="{avatar_url}" alt="avatar">
    <div class="user-info">
        <strong>{name}</strong>
        {email}
    </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"👤 **{name}**  \n`{email}`")
        
        if st.button("🚪 Đăng xuất", use_container_width=True):
            # Reset toàn bộ session
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_name = ""
            st.session_state.user_avatar = ""
            st.session_state.da_tai_lich_su = False
            st.session_state.lich_su = khoi_tao_lich_su()
            st.session_state.hien_thi = []
            st.rerun()
    else:
        # Chưa đăng nhập - hiển thị nút đăng nhập Google
        st.markdown("**👤 Tài khoản**")
        
        if kiem_tra_cau_hinh():
            login_url = tao_url_dang_nhap()
            # Dùng HTML link để redirect đến Google OAuth
            st.markdown(f"""
<a href="{login_url}" target="_self" class="google-btn">
    <svg width="18" height="18" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
    </svg>
    Đăng nhập bằng Google
</a>
""", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:0.78rem;color:#64748B;margin-top:0.4rem;'>Đăng nhập để lưu lịch sử trò chuyện</div>",
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ Chưa cấu hình Google OAuth trong `.env`")
    
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Theme toggle logic
    theme_label = "🌙 Chế độ Tối" if st.session_state.theme == "light" else "☀️ Chế độ Sáng"
    if st.button(theme_label, use_container_width=True):
        if st.session_state.theme == "light":
            st.session_state.theme = "dark"
        else:
            st.session_state.theme = "light"
        st.rerun()

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown("### Tôi có thể giúp gì?")
    st.markdown("""
- **Lộ trình học tập** ngành CNTT
- **Ngôn ngữ lập trình** nên học gì
- **Công cụ & IDE** phổ biến
- **Nghề nghiệp IT** & mức lương
- **Tài nguyên học** miễn phí
- **Giải đáp thắc mắc** năm nhất
    """)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown("### Câu hỏi gợi ý")
    goi_y = [
        "Năm nhất nên học ngôn ngữ gì?",
        "Lộ trình trở thành Web Developer?",
        "Không giỏi Toán có học IT được không?",
        "Git là gì và tại sao cần học?",
        "Data Science lương bao nhiêu?",
    ]
    for cau_hoi in goi_y:
        if st.button(cau_hoi, key=f"goi_y_{cau_hoi}", use_container_width=True):
            st.session_state.cau_hoi_goi_y = cau_hoi

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.lich_su = khoi_tao_lich_su()
        st.session_state.hien_thi = []
        st.rerun()


# ─── Header ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("assets/logo.png", width=100)
    except:
        st.write("🤖")
with col2:
    st.markdown("""
    <div class="itbot-header" style="text-align: left; padding: 0;">
        <h1 style="margin: 0;">ITBot</h1>
        <p style="margin: 0;">Trợ lý AI thân thiện cho sinh viên ngành Công nghệ Thông tin</p>
    </div>
    """, unsafe_allow_html=True)


# ─── Banner đăng nhập (nếu chưa đăng nhập) ───────────────────────────────────
if not st.session_state.logged_in and not st.session_state.hien_thi:
    st.markdown("""
<div class="welcome-box">
    <strong>Xin chào, tân sinh viên CNTT!</strong><br><br>
    Mình là <strong>ITBot</strong> – trợ lý AI được thiết kế để hỗ trợ
    các bạn SV năm nhất khám phá ngành Công nghệ Thông tin.<br><br>
    💡 <em>Đăng nhập bằng Google (sidebar bên trái) để lưu lịch sử trò chuyện của bạn.</em><br><br>
    Hãy hỏi mình bất cứ điều gì về:<br>
    • Lộ trình học tập &nbsp;•&nbsp; Ngôn ngữ lập trình &nbsp;•&nbsp;
    Nghề nghiệp IT &nbsp;•&nbsp; Kỹ năng cần thiết
</div>
""", unsafe_allow_html=True)
elif not st.session_state.hien_thi:
    st.markdown("""
<div class="welcome-box">
    <strong>Xin chào, tân sinh viên CNTT!</strong><br><br>
    Mình là <strong>ITBot</strong> – trợ lý AI được thiết kế để hỗ trợ
    các bạn SV năm nhất khám phá ngành Công nghệ Thông tin.<br><br>
    Hãy hỏi mình bất cứ điều gì bạn thắc mắc về:<br>
    • Lộ trình học tập &nbsp;•&nbsp; Ngôn ngữ lập trình &nbsp;•&nbsp;
    Nghề nghiệp IT &nbsp;•&nbsp; Kỹ năng cần thiết
</div>
""", unsafe_allow_html=True)


# ─── Hiển thị lịch sử chat ───────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for tin in st.session_state.hien_thi:
        if tin["role"] == "user":
            st.markdown(f"""
<div class="bubble-user">
    <div class="bubble-content">{tin["content"]}</div>
</div>
""", unsafe_allow_html=True)
            if tin.get("image"):
                 st.image(tin["image"], width=300)
        else:
            st.markdown(f"""
<div class="bubble-ai">
    <div class="avatar">🤖</div>
    <div class="bubble-content">{tin["content"]}</div>
</div>
""", unsafe_allow_html=True)


# ─── Input người dùng ────────────────────────────────────────────────────────
st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

def _on_enter():
    """Callback khi người dùng nhấn Enter trong ô input."""
    if st.session_state.input_tin_nhan.strip() or st.session_state.anh_tai_len:
        st.session_state.da_gui = True

# Add image uploader directly above chat input
anh_tai_len = st.file_uploader("Đính kèm hình ảnh (Bài tập/Câu hỏi)", type=["png", "jpg", "jpeg"], key="anh_tai_len")

col1, col2 = st.columns([5, 1])
with col1:
    # Nếu người dùng bấm câu hỏi gợi ý, điền sẵn vào input
    gia_tri_mac_dinh = st.session_state.pop("cau_hoi_goi_y", "")
    tin_nhan = st.text_input(
        label="Nhập tin nhắn",
        value=gia_tri_mac_dinh,
        placeholder="Hỏi mình về ngành IT, lộ trình học, nghề nghiệp, bài tập...",
        label_visibility="collapsed",
        key="input_tin_nhan",
        on_change=_on_enter,
    )
with col2:
    gui = st.button("Gửi", use_container_width=True)
    if gui and (tin_nhan.strip() or anh_tai_len):
        st.session_state.da_gui = True


# ─── Xử lý gửi tin nhắn ──────────────────────────────────────────────────────
if st.session_state.da_gui and (tin_nhan.strip() or anh_tai_len):
    noi_dung_nguoi_dung = tin_nhan.strip() if tin_nhan.strip() else "Hãy xem bức ảnh này."
    
    # Process image if uploaded
    hinh_anh = None
    if anh_tai_len:
         from PIL import Image
         hinh_anh = Image.open(anh_tai_len)

    # Reset cờ NGAY để tránh lặp
    st.session_state.da_gui = False

    # Thêm vào lịch sử hiển thị
    st.session_state.hien_thi.append({
        "role": "user",
        "content": noi_dung_nguoi_dung,
        "image": hinh_anh
    })

    # Lưu tin nhắn user vào database (nếu đã đăng nhập)
    if st.session_state.logged_in:
        add_message(st.session_state.user_email, "user", noi_dung_nguoi_dung)

    # Gọi AI
    with st.spinner("🤖 ITBot đang suy nghĩ..."):
        tra_loi = chat_voi_ai(st.session_state.lich_su, noi_dung_nguoi_dung, hinh_anh)

    # Cập nhật lịch sử Gemini SDK
    st.session_state.lich_su = them_vao_lich_su(
        st.session_state.lich_su, "user", noi_dung_nguoi_dung, hinh_anh
    )
    st.session_state.lich_su = them_vao_lich_su(
        st.session_state.lich_su, "model", tra_loi
    )

    # Thêm phản hồi vào lịch sử hiển thị
    st.session_state.hien_thi.append({
        "role": "assistant",
        "content": tra_loi
    })
    
    # Lưu phản hồi AI vào database (nếu đã đăng nhập)
    if st.session_state.logged_in:
        add_message(st.session_state.user_email, "model", tra_loi)

    st.rerun()
