"""
build_index.py - Script khởi tạo ChromaDB vector index từ toàn bộ PDF bài giảng.

Chạy 1 lần duy nhất (hoặc khi có PDF mới):
    python build_index.py

Sau khi chạy xong, file vector_store/ sẽ được tạo và chatbot tự động dùng.
"""

import sys
import time
from pathlib import Path

# Fix encoding cho Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    print("=" * 60)
    print("  BUILD VECTOR INDEX CHO ITBOT")
    print("=" * 60)
    print()

    # ── Kiểm tra thư mục PDF ────────────────────────────────────────
    tu_muc_lectures = Path(__file__).parent / "data" / "lectures"
    if not tu_muc_lectures.exists():
        print(f"[LOI] Khong tim thay thu muc: {tu_muc_lectures}")
        print("      Hay kiem tra lai duong dan data/lectures/")
        sys.exit(1)

    tat_ca_pdf = list(tu_muc_lectures.rglob("*.pdf"))
    if not tat_ca_pdf:
        print(f"[LOI] Khong co file PDF nao trong: {tu_muc_lectures}")
        sys.exit(1)

    print(f"[OK] Thu muc: {tu_muc_lectures}")
    print(f"[OK] Tim thay {len(tat_ca_pdf)} file PDF\n")

    # ── Hỏi người dùng nếu index đã tồn tại ────────────────────────
    from rag.indexer import da_co_index, VECTOR_STORE_DIR

    if da_co_index():
        print("[WARN] Vector store da ton tai!")
        print(f"       Thu muc: {VECTOR_STORE_DIR}")
        lua_chon = input("\nBan co muon xay dung lai tu dau? [y/N]: ").strip().lower()
        xoa_cu = lua_chon in ('y', 'yes')
        if not xoa_cu:
            print("\n[INFO] Giu nguyen index hien tai. Thoat.")
            return
        print()

    else:
        xoa_cu = True

    # ── Bước 1: Extract PDF ─────────────────────────────────────────
    print("BUOC 1/2: EXTRACT TEXT TU PDF")
    print("-" * 40)

    t0 = time.time()
    from rag.extract_pdf import extract_tat_ca
    chunks = extract_tat_ca(hien_thi_tien_trinh=True)
    t1 = time.time()

    if not chunks:
        print("[LOI] Khong extract duoc chunk nao! Kiem tra lai file PDF.")
        sys.exit(1)

    print(f"      Thoi gian: {t1 - t0:.1f} giay\n")

    # ── Bước 2: Tạo index ───────────────────────────────────────────
    print("BUOC 2/2: TAO VECTOR INDEX (FAISS)")
    print("-" * 40)
    print("[INFO] Dang load embedding model lan dau (co the mat vai phut)...")
    print("       Model: paraphrase-multilingual-MiniLM-L12-v2 (~120 MB)\n")

    t2 = time.time()
    from rag.indexer import tao_index
    tao_index(chunks, xoa_cu=xoa_cu)
    t3 = time.time()

    print(f"      Thoi gian: {t3 - t2:.1f} giay\n")

    # ── Tổng kết ────────────────────────────────────────────────────
    tong_thoi_gian = t3 - t0
    print("=" * 60)
    print("  HOAN TAT!")
    print("=" * 60)
    print(f"  Tong thoi gian : {tong_thoi_gian:.0f} giay ({tong_thoi_gian/60:.1f} phut)")
    print(f"  Tong chunks    : {len(chunks):,}")
    print(f"  Vector store   : {VECTOR_STORE_DIR}")
    print()
    print("  Bot da san sang dung RAG!")
    print("  Chay: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
