"""
indexer.py - Tạo và lưu FAISS vector index từ các PDF chunks.

Dùng FAISS (faiss-cpu) thay ChromaDB vì FAISS tương thích tốt hơn với Python 3.13.
Chạy 1 lần duy nhất qua build_index.py để khởi tạo vector store.
"""

import faiss
import numpy as np
import json
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import Optional

# ─── Cấu hình ────────────────────────────────────────────────────────────────

# Model embedding đa ngôn ngữ, hỗ trợ tiếng Việt tốt (~120 MB)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Kích thước vector của model trên (384 chiều)
EMBEDDING_DIM = 384

# Thư mục lưu FAISS vector store
VECTOR_STORE_DIR = Path(__file__).parent.parent / "data" / "vector_store"

# Tên file index và metadata
FAISS_INDEX_FILE = VECTOR_STORE_DIR / "index.faiss"
METADATA_FILE = VECTOR_STORE_DIR / "metadata.pkl"

# Số chunks xử lý mỗi batch (tránh tràn RAM)
BATCH_SIZE = 64


# ─── Singleton model (load 1 lần, tái dùng cho cả indexer và retriever) ──────
_model: Optional[SentenceTransformer] = None


def lay_model() -> SentenceTransformer:
    """Load embedding model (lazy loading - chỉ load lần đầu dùng)."""
    global _model
    if _model is None:
        print(f"[INFO] Đang load embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("[OK] Model đã sẵn sàng.")
    return _model


def da_co_index() -> bool:
    """Kiểm tra xem vector store đã được build chưa."""
    return FAISS_INDEX_FILE.exists() and METADATA_FILE.exists()


def _tao_embedding(texts: list[str]) -> np.ndarray:
    """
    Tạo normalized embeddings cho danh sách texts.
    Trả về numpy array shape (n, EMBEDDING_DIM).
    """
    model = lay_model()
    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True  # L2 normalize để dùng inner product = cosine
    )
    return embeddings.astype(np.float32)


def tao_index(chunks: list[dict], xoa_cu: bool = False) -> None:
    """
    Tạo FAISS vector index từ danh sách chunks và lưu vào disk.

    Args:
        chunks: List of {"id": str, "text": str, "metadata": dict}
        xoa_cu: Nếu True, xóa index cũ trước khi tạo mới
    """
    if not chunks:
        print("[WARN] Không có chunk nào để index!")
        return

    # Tạo thư mục lưu
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    # Xóa index cũ nếu cần
    if xoa_cu:
        if FAISS_INDEX_FILE.exists():
            FAISS_INDEX_FILE.unlink()
        if METADATA_FILE.exists():
            METADATA_FILE.unlink()
        print("[INFO] Đã xóa index cũ.")

    tong = len(chunks)
    print(f"\n[INFO] Bắt đầu index {tong:,} chunks (batch size = {BATCH_SIZE})...")
    print("[INFO] Dang load embedding model (co the mat vai phut lan dau)...")

    # Tạo FAISS index dùng inner product (= cosine khi đã normalize)
    faiss_index = faiss.IndexFlatIP(EMBEDDING_DIM)

    # Lưu text và metadata song song với vector index
    all_texts = []
    all_metadata = []

    da_xu_ly = 0

    for batch_start in range(0, tong, BATCH_SIZE):
        batch = chunks[batch_start: batch_start + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        metadatas = [c["metadata"] for c in batch]

        try:
            embeddings = _tao_embedding(texts)
            faiss_index.add(embeddings)

            all_texts.extend(texts)
            all_metadata.extend(metadatas)

            da_xu_ly += len(batch)
            pct = da_xu_ly / tong * 100
            print(f"  [{da_xu_ly:,}/{tong:,}] {pct:.1f}% hoan thanh", end='\r')

        except Exception as e:
            print(f"\n  [WARN] Loi batch {batch_start}: {e}")

    print()  # Xuống dòng sau progress

    # Lưu FAISS index
    faiss.write_index(faiss_index, str(FAISS_INDEX_FILE))

    # Lưu metadata và texts bằng pickle
    store = {"texts": all_texts, "metadatas": all_metadata}
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(store, f)

    print(f"\n[OK] Index hoan tat!")
    print(f"     Đã index: {da_xu_ly:,} vectors")
    print(f"     Lưu tại: {VECTOR_STORE_DIR}")
    print(f"     Index file: {FAISS_INDEX_FILE.name} ({FAISS_INDEX_FILE.stat().st_size // 1024:,} KB)")


def tai_index() -> tuple[faiss.Index, list[str], list[dict]]:
    """
    Load FAISS index và metadata từ disk.

    Returns:
        (faiss_index, texts, metadatas)
    Raises:
        FileNotFoundError nếu index chưa được build.
    """
    if not da_co_index():
        raise FileNotFoundError(
            f"Vector store chua duoc build! Chay: python build_index.py"
        )

    faiss_index = faiss.read_index(str(FAISS_INDEX_FILE))

    with open(METADATA_FILE, "rb") as f:
        store = pickle.load(f)

    return faiss_index, store["texts"], store["metadatas"]
