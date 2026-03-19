"""
logic_ai.py - Bo nao cua chatbot
Su dung google-genai SDK (phien ban moi nhat).
Tich hop RAG: tu dong tim tai lieu lien quan tu ChromaDB truoc moi cau tra loi.
"""

import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import io

# Fix encoding cho Windows terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# --- Load bien moi truong tu .env -------------------------------------------
load_dotenv()


# --- Doc file ngu canh -------------------------------------------------------
def _doc_ngu_canh() -> str:
    """Doc noi dung file ngu_canh.txt lam system prompt."""
    duong_dan = Path(__file__).parent / "data" / "ngu_canh.txt"
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Ban la ITBot, tro ly AI ho tro sinh vien nganh CNTT."


# --- Lay Gemini client -------------------------------------------------------
def _lay_client() -> genai.Client:
    """Tao va tra ve Gemini Client da xac thuc."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "Chua co API Key!\n"
            "Mo file .env va thay 'your_api_key_here' bang API key that.\n"
            "Lay mien phi tai: https://aistudio.google.com/app/apikey"
        )
    return genai.Client(api_key=api_key)


# --- Tim tai lieu lien quan (RAG) --------------------------------------------
def _tim_tai_lieu_rag(cau_hoi: str) -> str:
    """
    Tim cac doan tai lieu lien quan den cau hoi tu vector store.
    Tra ve chuoi nguon tham khao, hoac '' neu chua build index.
    """
    try:
        from rag.retriever import tao_nguon_tham_khao
        return tao_nguon_tham_khao(cau_hoi)
    except ImportError:
        return ""  # RAG chua duoc cai dat
    except Exception:
        return ""  # Vector store chua ton tai hoac loi khac


# --- Khoi tao lich su chat ---------------------------------------------------
def khoi_tao_lich_su() -> list:
    """Tra ve lich su chat rong cho mot phien moi."""
    return []

def image_to_bytes(image: Image.Image) -> bytes:
    """Chuyen PIL Image sang bytes de truyen qua API."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


# --- Ham chat chinh ----------------------------------------------------------
def chat_voi_ai(lich_su_chat: list, tin_nhan_moi: str, hinh_anh=None) -> str:
    """
    Gui tin nhan den Gemini va tra ve cau tra loi dang string.
    Tu dong tim tai lieu lien quan qua RAG (neu vector store da ton tai).

    Args:
        lich_su_chat: Danh sach dict [{"role": "user"/"model", "parts": [str/image]}]
        tin_nhan_moi: Cau hoi moi cua nguoi dung
        hinh_anh: Doi tuong PIL.Image (Optional)

    Returns:
        Chuoi phan hoi tu AI, hoac thong bao loi.
    """
    try:
        client = _lay_client()
        ngu_canh = _doc_ngu_canh()

        # --- RAG: Tim tai lieu lien quan va ghep vao system prompt -----------
        # Tu dong them RAG doc neu co hinh anh de AI giai bai tap tu file PDF RAG
        nguon_rag = _tim_tai_lieu_rag(tin_nhan_moi)
        if nguon_rag:
            ngu_canh = ngu_canh + "\n\n" + nguon_rag
            
            if hinh_anh:
                 ngu_canh += "\n\n[Hệ thống ghi chú: Người dùng có gửi kèm 1 hình ảnh (có thể là bài tập). Hãy kết hợp hình ảnh này với ngữ cảnh RAG ở trên để giải hoặc phân tích chi tiết.]"
        # ---------------------------------------------------------------------

        # Chuyển đổi lịch sử chat (list of dict) sang list of types.Content
        contents = []
        for luot in lich_su_chat:
             parts = []
             for p in luot["parts"]:
                 if isinstance(p, str):
                     parts.append(types.Part.from_text(text=p))
                 elif isinstance(p, Image.Image):
                     parts.append(types.Part(
                         inline_data=types.Blob(
                             mime_type="image/jpeg",
                             data=image_to_bytes(p)
                         )
                     ))
                 # SDK might have some parts already as objects if coming from response
                 elif hasattr(p, 'text') or hasattr(p, 'inline_data'):
                     parts.append(p)
             
             contents.append(
                types.Content(role=luot["role"], parts=parts)
             )

        # Chuẩn bị nội dung gửi đi (User Parts)
        user_parts = [types.Part.from_text(text=tin_nhan_moi)]
        if hinh_anh:
             user_parts.append(types.Part(
                 inline_data=types.Blob(
                     mime_type="image/jpeg",
                     data=image_to_bytes(hinh_anh)
                 )
             ))
             
        contents.append(
            types.Content(
                role="user",
                parts=user_parts
            )
        )

        # Goi SDK với model ổn định nhất (Gemini Flash Latest)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=ngu_canh,
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=2048,
            )
        )
        return response.text

    except ValueError as e:
        return f"Lỗi cấu hình: {str(e)}"
    except Exception as e:
        loi_str = str(e)
        if "429" in loi_str or "RESOURCE_EXHAUSTED" in loi_str:
            return (
                "⚠️ **Thông báo: Hết lượt sử dụng miễn phí hôm nay.**\n\n"
                "Bạn đã vượt quá giới hạn yêu cầu (quota) của Google Gemini dành cho tài khoản miễn phí. "
                "Vui lòng đợi một lát (khoảng 1 phút) hoặc quay lại sau nhé. \n\n"
                "Nếu bạn tự cài đặt API Key cá nhân, hãy kiểm tra hạn mức tại [Google AI Studio](https://aistudio.google.com/)."
            )
        return (
            f"Có lỗi xảy ra khi kết nối AI:\n{loi_str}\n\n"
            "Vui lòng kiểm tra lại API Key trong file .env."
        )


# --- Cap nhat lich su --------------------------------------------------------
def them_vao_lich_su(lich_su: list, vai_tro: str, noi_dung: str = None, hinh_anh=None) -> list:
    """
    Them mot luot trao doi vao lich su chat.
    """
    parts = []
    if noi_dung:
        parts.append(noi_dung)
    if hinh_anh:
        parts.append(hinh_anh)
        
    lich_su.append({
        "role": vai_tro,
        "parts": parts
    })
    return lich_su
