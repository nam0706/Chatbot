"""
retriever.py - Tìm kiếm tài liệu liên quan theo câu hỏi của người dùng.

Dùng FAISS semantic search để tìm top-K chunks gần nhất với câu hỏi.
"""

import numpy as np
from typing import Optional
from rag.indexer import (
    lay_model, da_co_index, tai_index,
    VECTOR_STORE_DIR
)

# ─── Cache index trong RAM (tránh đọc file mỗi lần hỏi) ─────────────────────
_cache: Optional[tuple] = None   # (faiss_index, texts, metadatas)


def _lay_index():
    """Load và cache FAISS index vào RAM."""
    global _cache
    if _cache is None and da_co_index():
        try:
            _cache = tai_index()
        except Exception as e:
            print(f"[WARN] Khong load duoc index: {e}")
            return None
    return _cache


# ─── Cấu hình tìm kiếm ───────────────────────────────────────────────────────
TOP_K_MAC_DINH = 4
NGUONG_DO_TUONG_TU = 0.30    # Ngưỡng cosine similarity (0-1)
MAX_DO_DAI_NGUON = 1500      # Giới hạn ký tự ghép vào system prompt


def tim_tai_lieu(cau_hoi: str, top_k: int = TOP_K_MAC_DINH) -> list[dict]:
    """
    Tìm top-K tài liệu liên quan nhất với câu hỏi.

    Args:
        cau_hoi: Câu hỏi của người dùng
        top_k: Số tài liệu muốn lấy

    Returns:
        List of {"text": str, "metadata": dict, "score": float}
        Trả về [] nếu vector store chưa tồn tại hoặc không tìm thấy.
    """
    index_data = _lay_index()
    if index_data is None:
        return []

    faiss_index, texts, metadatas = index_data

    try:
        model = lay_model()

        # Encode câu hỏi với cùng model, chuẩn hóa để dùng cosine
        query_embedding = model.encode(
            [cau_hoi],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype(np.float32)

        # Tìm top-K gần nhất trong FAISS
        k = min(top_k, faiss_index.ntotal)
        if k == 0:
            return []

        scores, indices = faiss_index.search(query_embedding, k)

        # Lọc theo ngưỡng và chuyển sang format dễ dùng
        tai_lieu = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(texts):
                continue
            do_tuong_tu = float(score)  # Đã normalize → inner product = cosine
            if do_tuong_tu >= NGUONG_DO_TUONG_TU:
                tai_lieu.append({
                    "text": texts[idx],
                    "metadata": metadatas[idx],
                    "score": round(do_tuong_tu, 4)
                })

        return tai_lieu

    except Exception as e:
        print(f"[WARN] Loi khi tim kiem tai lieu: {e}")
        return []


def _format_metadata(meta: dict) -> str:
    """Format metadata thành chuỗi mô tả nguồn tài liệu."""
    phan = []
    if meta.get("mon_hoc"):
        phan.append(f"{meta.get('ma_mon', '')} {meta.get('mon_hoc', '')}".strip())
    if meta.get("loai"):
        loai_map = {
            "slide_bai_giang": "Slide bài giảng",
            "de_thi": "Đề thi",
            "thuc_hanh": "Thực hành",
            "sach_tham_khao": "Sách tham khảo",
            "bai_giang": "Bài giảng",
        }
        phan.append(loai_map.get(meta["loai"], meta["loai"]))
    if meta.get("nam_hoc"):
        phan.append(meta["nam_hoc"])
    return " | ".join(phan) if phan else "Tài liệu bài giảng"


def tao_nguon_tham_khao(cau_hoi: str, top_k: int = TOP_K_MAC_DINH) -> str:
    """
    Tạo chuỗi "Tài liệu tham khảo" để ghép vào system prompt của Gemini.

    Returns:
        Chuỗi văn bản chứa đoạn tài liệu liên quan, hoặc "" nếu không có.
    """
    tai_lieu = tim_tai_lieu(cau_hoi, top_k)
    if not tai_lieu:
        return ""

    dong = [
        "================================================================",
        "TAI LIEU THAM KHAO TU BAI GIANG (Relevant lecture excerpts)",
        "Hay uu tien su dung thong tin nay khi tra loi cau hoi lien quan.",
        "================================================================",
    ]

    tong_do_dai = sum(len(d) for d in dong)

    for i, item in enumerate(tai_lieu, 1):
        nguon = _format_metadata(item["metadata"])
        tieu_de = f"\n[Doan {i}] Nguon: {nguon} (do lien quan: {item['score']:.0%})"
        noi_dung = item["text"]

        neu_them = len(tieu_de) + len(noi_dung)
        if tong_do_dai + neu_them > MAX_DO_DAI_NGUON:
            con_lai = MAX_DO_DAI_NGUON - tong_do_dai - len(tieu_de) - 5
            if con_lai > 100:
                dong.append(tieu_de)
                dong.append(noi_dung[:con_lai] + "...")
            break

        dong.append(tieu_de)
        dong.append(noi_dung)
        tong_do_dai += neu_them

    dong.append("\n================================================================")
    return '\n'.join(dong)
