"""
kiem_tra_logic.py - File test nhanh danh cho lap trinh vien
Chay file nay de kiem tra ket noi Gemini API ma khong can Streamlit.

Cach dung:
    python kiem_tra_logic.py
"""

import sys
import io

# Fix encoding cho Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from logic_ai import chat_voi_ai, khoi_tao_lich_su, them_vao_lich_su


def kiem_tra_ket_noi():
    """Kiem tra xem API key co hop le va ket noi duoc voi Gemini khong."""
    print("=" * 60)
    print("  KIEM TRA KET NOI GOOGLE GEMINI API")
    print("=" * 60)

    lich_su = khoi_tao_lich_su()
    cau_hoi = "Xin chao! Hay gioi thieu ngan gon ve ban than trong 2 cau."

    print(f"\nCau hoi test: {cau_hoi}\n")
    print("Dang ket noi den Gemini API...")

    tra_loi = chat_voi_ai(lich_su, cau_hoi)

    print("\nPhan hoi tu AI:")
    print("-" * 40)
    print(tra_loi)
    print("-" * 40)

    if tra_loi.startswith("Loi") or tra_loi.startswith("Co loi"):
        print("\n[THAT BAI] Co loi xay ra (xem thong bao phia tren)")
    else:
        print("\n[THANH CONG] API hoat dong binh thuong!")


def kiem_tra_hoi_dap_nhieu_luot():
    """Kiem tra kha nang nho ngu canh trong nhieu luot hoi thoai."""
    print("\n" + "=" * 60)
    print("  KIEM TRA HOI THOAI NHIEU LUOT (MEMORY TEST)")
    print("=" * 60)

    lich_su = khoi_tao_lich_su()

    cac_cau_hoi = [
        "Python co phu hop cho nguoi moi hoc khong?",
        "Vay toi nen bat dau tu dau?",
        "Cam on! Cau hoi dau tien toi hoi la gi?",
    ]

    for i, cau_hoi in enumerate(cac_cau_hoi, 1):
        print(f"\n[Luot {i}] User: {cau_hoi}")
        tra_loi = chat_voi_ai(lich_su, cau_hoi)

        lich_su = them_vao_lich_su(lich_su, "user", cau_hoi)
        lich_su = them_vao_lich_su(lich_su, "model", tra_loi)

        hien_thi = tra_loi[:250] + "..." if len(tra_loi) > 250 else tra_loi
        print(f"[Luot {i}] AI: {hien_thi}")

    print(f"\n[OK] Hoan thanh test {len(cac_cau_hoi)} luot hoi thoai!")
    print(f"   Tong so luot trong lich su: {len(lich_su)}")


if __name__ == "__main__":
    kiem_tra_ket_noi()
    # kiem_tra_hoi_dap_nhieu_luot()  # Bo comment de test nhieu luot

    print("\n" + "=" * 60)
    print("  XONG! Neu khong co loi, hay chay: streamlit run app.py")
    print("=" * 60)
