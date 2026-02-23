"""
logic_ai.py - Bo nao cua chatbot
Su dung google-genai SDK (phien ban moi nhat).
"""

import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

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


# --- Khoi tao lich su chat ---------------------------------------------------
def khoi_tao_lich_su() -> list:
    """Tra ve lich su chat rong cho mot phien moi."""
    return []


# --- Ham chat chinh ----------------------------------------------------------
def chat_voi_ai(lich_su_chat: list, tin_nhan_moi: str) -> str:
    """
    Gui tin nhan den Gemini va tra ve cau tra loi dang string.

    Args:
        lich_su_chat: Danh sach dict [{"role": "user"/"model", "parts": [str]}]
        tin_nhan_moi: Cau hoi moi cua nguoi dung

    Returns:
        Chuoi phan hoi tu AI, hoac thong bao loi.
    """
    try:
        client = _lay_client()
        ngu_canh = _doc_ngu_canh()

        # Xay dung contents tu lich su chat
        contents = []
        for luot in lich_su_chat:
            contents.append(
                types.Content(
                    role=luot["role"],
                    parts=[types.Part(text=p) for p in luot["parts"]]
                )
            )

        # Them tin nhan moi cua user
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=tin_nhan_moi)]
            )
        )

        # Goi API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=ngu_canh,
                temperature=0.8,
                top_p=0.95,
                max_output_tokens=2048,
            )
        )
        return response.text

    except ValueError as e:
        return f"Loi cau hinh: {str(e)}"
    except Exception as e:
        return (
            f"Co loi xay ra khi ket noi AI:\n{str(e)}\n\n"
            "Vui long kiem tra lai API Key trong file .env."
        )


# --- Cap nhat lich su --------------------------------------------------------
def them_vao_lich_su(lich_su: list, vai_tro: str, noi_dung: str) -> list:
    """
    Them mot luot trao doi vao lich su chat.

    Args:
        lich_su: Danh sach lich su hien tai
        vai_tro: 'user' hoac 'model'
        noi_dung: Noi dung tin nhan

    Returns:
        Danh sach lich su da cap nhat
    """
    lich_su.append({
        "role": vai_tro,
        "parts": [noi_dung]
    })
    return lich_su
