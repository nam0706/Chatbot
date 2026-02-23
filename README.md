# 🤖 ITBot - Trợ Lý AI Ngành Công Nghệ Thông Tin

> Chatbot AI thân thiện hỗ trợ sinh viên năm nhất ngành CNTT  
> Powered by **Google Gemini 1.5 Flash** + **Streamlit**

---

## 📸 Tính năng

- 💬 Hội thoại tự nhiên với AI về mọi chủ đề ngành IT
- 🗺️ Tư vấn lộ trình học tập cho SV năm nhất
- 💼 Thông tin nghề nghiệp, mức lương, kỹ năng cần thiết
- 📚 Gợi ý tài nguyên học miễn phí
- 🎨 Giao diện Dark Tech đẹp mắt, có lịch sử chat
- ❓ Câu hỏi gợi ý nhanh ở Sidebar

---

## 🚀 Hướng dẫn cài đặt & chạy

### Bước 1: Clone hoặc tải về dự án

```bash
git clone <url-repo-cua-ban>
cd du-an-chatbot
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Lấy API Key miễn phí

1. Truy cập: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Đăng nhập bằng tài khoản Google
3. Bấm **"Create API Key"** → Sao chép key

### Bước 5: Cấu hình API Key

Mở file `.env` và thay thế:

```env
GOOGLE_API_KEY=your_api_key_here
```

thành:

```env
GOOGLE_API_KEY=AIzaSy...key_cua_ban...
```

### Bước 6: Kiểm tra kết nối (tuỳ chọn)

```bash
python kiem_tra_logic.py
```

Kỳ vọng: AI trả lời câu hỏi test → kết nối thành công ✅

### Bước 7: Chạy ứng dụng

```bash
streamlit run app.py
```

Mở trình duyệt tại: [http://localhost:8501](http://localhost:8501)

---

## 📁 Cấu trúc dự án

```
du-an-chatbot/
├── .streamlit/
│   └── config.toml       # Dark tech theme
├── assets/               # Logo, ảnh minh họa
├── data/
│   └── ngu_canh.txt      # Kiến thức IT cho chatbot
├── .env                  # API Key (KHÔNG đẩy lên GitHub!)
├── .gitignore
├── requirements.txt
├── logic_ai.py           # Kết nối Gemini API
├── app.py                # Giao diện Streamlit
├── kiem_tra_logic.py     # File test nhanh
└── README.md
```

---

## ⚠️ Lưu ý bảo mật

- **KHÔNG BAO GIỜ** đẩy file `.env` lên GitHub
- File `.gitignore` đã chặn `.env` tự động
- Nếu vô tình đẩy key lên GitHub → xóa key cũ và tạo key mới ngay

---

## 🛠️ Thư viện sử dụng

| Thư viện | Phiên bản | Mục đích |
|----------|-----------|----------|
| streamlit | ≥1.32.0 | Giao diện web |
| google-generativeai | ≥0.5.0 | Gemini API |
| python-dotenv | ≥1.0.0 | Đọc file .env |

---

## 👨‍💻 Dành cho lập trình viên

**Tùy chỉnh kiến thức:** Chỉnh sửa `data/ngu_canh.txt` để thêm/bớt kiến thức.  
**Đổi model:** Trong `logic_ai.py`, thay `gemini-1.5-flash` bằng `gemini-1.5-pro` nếu muốn mạnh hơn.  
**Đổi theme:** Chỉnh màu sắc trong `.streamlit/config.toml`.

---

*Made with ❤️ for IT Students*
