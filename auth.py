"""
auth.py - Xử lý Google OAuth 2.0 cho ITBot
Dùng requests thuần túy, không cần thư viện phức tạp.
"""

import os
import json
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── Cấu hình OAuth ───────────────────────────────────────────────────────────
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def tao_url_dang_nhap() -> str:
    """
    Tạo URL redirect đến trang đăng nhập Google.
    Trả về URL dạng string để dùng với st.markdown redirect.
    """
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "select_account",
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)


def doi_code_lay_tokens(code: str) -> dict | None:
    """
    Đổi authorization code lấy access_token từ Google.
    Trả về dict chứa access_token, hoặc None nếu lỗi.
    """
    try:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[auth] Lỗi đổi code lấy token: {e}")
        return None


def lay_thong_tin_nguoi_dung(access_token: str) -> dict | None:
    """
    Gọi Google UserInfo API để lấy email, tên, avatar.
    Trả về dict: {email, name, picture}, hoặc None nếu lỗi.
    """
    try:
        response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "email": data.get("email", ""),
            "name": data.get("name", "Người dùng"),
            "picture": data.get("picture", ""),
        }
    except Exception as e:
        print(f"[auth] Lỗi lấy thông tin user: {e}")
        return None


def kiem_tra_cau_hinh() -> bool:
    """Kiểm tra xem OAuth đã được cấu hình chưa."""
    return bool(CLIENT_ID and CLIENT_SECRET)
