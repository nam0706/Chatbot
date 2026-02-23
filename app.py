"""
app.py - Giao diện Streamlit cho IT Chatbot
Thân xác của chatbot: dark tech theme, bubble chat, lịch sử hội thoại.
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

# ─── CSS Tuỳ chỉnh (Dark Tech Theme) ────────────────────────────────────────
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0A0E1A 0%, #0D1117 50%, #0A0E1A 100%);
}

/* Header */
.itbot-header {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    margin-bottom: 1rem;
}
.itbot-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00D4FF, #7B2FFF, #00D4FF);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shine 3s linear infinite;
    margin: 0;
}
@keyframes shine {
    to { background-position: 200% center; }
}
.itbot-header p {
    color: #64748B;
    font-size: 0.95rem;
    margin: 0.3rem 0 0 0;
}

/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    padding: 0.5rem 0;
}

/* Chat bubbles */
.bubble-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
    gap: 0.5rem;
    animation: slideInRight 0.3s ease;
}
.bubble-user .bubble-content {
    background: linear-gradient(135deg, #7B2FFF, #5B21B6);
    color: #fff;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(123,47,255,0.3);
}

.bubble-ai {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 0.5rem;
    animation: slideInLeft 0.3s ease;
}
.bubble-ai .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00D4FF, #0099BB);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(0,212,255,0.4);
}
.bubble-ai .bubble-content {
    background: linear-gradient(135deg, #111827, #1F2937);
    color: #E2E8F0;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 80%;
    font-size: 0.95rem;
    line-height: 1.6;
    border: 1px solid rgba(0,212,255,0.15);
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* Input area */
.stTextInput > div > div > input {
    background: #111827 !important;
    border: 1.5px solid rgba(0,212,255,0.3) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF, #0099BB) !important;
    color: #0A0E1A !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,212,255,0.4) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #111827 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.1) !important;
}

/* Welcome box */
.welcome-box {
    background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,255,0.08));
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    color: #94A3B8;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* Divider */
.custom-divider {
    border: none;
    border-top: 1px solid rgba(0,212,255,0.15);
    margin: 1rem 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0A0E1A; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─── Khởi tạo Session State ──────────────────────────────────────────────────
if "lich_su" not in st.session_state:
    st.session_state.lich_su = khoi_tao_lich_su()

if "hien_thi" not in st.session_state:
    # Lưu lịch sử để hiển thị (role: "user"/"assistant", content: str)
    st.session_state.hien_thi = []

if "da_gui" not in st.session_state:
    st.session_state.da_gui = False


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 ITBot")
    st.markdown("*Trợ lý AI ngành Công nghệ Thông tin*")
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown("### 💡 Tôi có thể giúp gì?")
    st.markdown("""
- 🗺️ **Lộ trình học tập** ngành CNTT
- 💻 **Ngôn ngữ lập trình** nên học gì
- 🛠️ **Công cụ & IDE** phổ biến
- 💼 **Nghề nghiệp IT** & mức lương
- 📚 **Tài nguyên học** miễn phí
- ❓ **Giải đáp thắc mắc** năm nhất
    """)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown("### ✨ Câu hỏi gợi ý")
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#475569;font-size:0.78rem;text-align:center;'>"
        "Powered by Google Gemini 1.5 Flash<br>"
        "Made with ❤️ for IT Students"
        "</div>",
        unsafe_allow_html=True
    )


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="itbot-header">
    <h1>🤖 ITBot</h1>
    <p>Trợ lý AI thân thiện cho sinh viên ngành Công nghệ Thông tin</p>
</div>
""", unsafe_allow_html=True)


# ─── Màn hình chào (khi chưa có chat) ───────────────────────────────────────
if not st.session_state.hien_thi:
    st.markdown("""
<div class="welcome-box">
    👋 <strong>Xin chào, tân sinh viên CNTT!</strong><br><br>
    Mình là <strong>ITBot</strong> – trợ lý AI được thiết kế đặc biệt để hỗ trợ
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
    <span style="font-size:1.4rem;">👤</span>
</div>
""", unsafe_allow_html=True)
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
    if st.session_state.input_tin_nhan.strip():
        st.session_state.da_gui = True

col1, col2 = st.columns([5, 1])
with col1:
    # Nếu người dùng bấm câu hỏi gợi ý, điền sẵn vào input
    gia_tri_mac_dinh = st.session_state.pop("cau_hoi_goi_y", "")
    tin_nhan = st.text_input(
        label="Nhập tin nhắn",
        value=gia_tri_mac_dinh,
        placeholder="💬 Hỏi mình về ngành IT, lộ trình học, nghề nghiệp...",
        label_visibility="collapsed",
        key="input_tin_nhan",
        on_change=_on_enter,
    )
with col2:
    gui = st.button("Gửi ➤", use_container_width=True)
    if gui and tin_nhan.strip():
        st.session_state.da_gui = True


# ─── Xử lý gửi tin nhắn ──────────────────────────────────────────────────────
if st.session_state.da_gui and tin_nhan.strip():
    noi_dung_nguoi_dung = tin_nhan.strip()

    # Reset cờ NGAY để tránh lặp
    st.session_state.da_gui = False

    # Thêm vào lịch sử hiển thị
    st.session_state.hien_thi.append({
        "role": "user",
        "content": noi_dung_nguoi_dung
    })

    # Gọi AI
    with st.spinner("🤖 ITBot đang suy nghĩ..."):
        tra_loi = chat_voi_ai(st.session_state.lich_su, noi_dung_nguoi_dung)

    # Cập nhật lịch sử Gemini SDK
    st.session_state.lich_su = them_vao_lich_su(
        st.session_state.lich_su, "user", noi_dung_nguoi_dung
    )
    st.session_state.lich_su = them_vao_lich_su(
        st.session_state.lich_su, "model", tra_loi
    )

    # Thêm phản hồi vào lịch sử hiển thị
    st.session_state.hien_thi.append({
        "role": "assistant",
        "content": tra_loi
    })

    st.rerun()
