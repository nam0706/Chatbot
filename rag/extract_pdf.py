"""
extract_pdf.py - Đọc toàn bộ PDF trong data/lectures/ và chia thành chunks.

Cách dùng:
    from rag.extract_pdf import extract_tat_ca
    chunks = extract_tat_ca()
    # chunks = [{"text": "...", "id": "...", "metadata": {...}}, ...]
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import Generator

# ─── Cấu hình chunk ──────────────────────────────────────────────────────────
CHUNK_SIZE = 500      # Số ký tự mỗi chunk
CHUNK_OVERLAP = 100   # Số ký tự overlap giữa các chunk liên tiếp
MIN_CHUNK_LEN = 80    # Bỏ các chunk quá ngắn (không có thông tin hữu ích)

# ─── Đường dẫn gốc đến thư mục bài giảng ────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data" / "lectures"


def _lam_sach_text(text: str) -> str:
    """Xóa khoảng trắng thừa và ký tự không cần thiết từ text PDF."""
    # Gộp nhiều dòng trắng thành 1
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Xóa khoảng trắng thừa đầu/cuối dòng
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(lines)
    # Xóa khoảng trắng đầu cuối toàn bộ
    return text.strip()


def _chia_chunks(text: str, chunk_size: int = CHUNK_SIZE,
                  overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Chia text thành các chunks có kích thước cố định với overlap.
    Ưu tiên cắt tại ranh giới câu (dấu . ! ?) hoặc dòng mới.
    """
    if len(text) <= chunk_size:
        return [text] if len(text) >= MIN_CHUNK_LEN else []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end >= len(text):
            # Chunk cuối
            chunk = text[start:].strip()
            if len(chunk) >= MIN_CHUNK_LEN:
                chunks.append(chunk)
            break

        # Tìm điểm cắt tự nhiên: dòng mới hoặc dấu câu
        cut = end
        for sep in ['\n\n', '\n', '. ', '! ', '? ', ' ']:
            idx = text.rfind(sep, start + overlap, end)
            if idx != -1:
                cut = idx + len(sep)
                break

        chunk = text[start:cut].strip()
        if len(chunk) >= MIN_CHUNK_LEN:
            chunks.append(chunk)

        start = cut - overlap  # Overlap để giữ ngữ cảnh

    return chunks


def _phan_loai_tai_lieu(duong_dan: Path) -> dict:
    """
    Phân loại tài liệu dựa trên đường dẫn thư mục:
    Trả về metadata gồm: mon_hoc, ma_mon, loai, nam_hoc
    """
    parts = duong_dan.parts

    # Tìm tên môn học (thư mục dạng "IT001. Nhập môn lập trình")
    mon_hoc = ""
    ma_mon = ""
    for part in parts:
        p = str(part)
        # Pattern: "IT001. Tên môn" hoặc "MA003. Tên môn" hoặc "SS006. Tên môn"
        ma = re.match(r'^([A-Z]{2}\d{3})\.?\s*(.+)$', p)
        if ma:
            ma_mon = ma.group(1)
            mon_hoc = ma.group(2).strip()
            break

    # Xác định loại tài liệu
    loai = "bai_giang"
    duong_dan_str = str(duong_dan).lower()
    if any(kw in duong_dan_str for kw in ['đề thi', 'de thi', 'dapan', 'thi']):
        loai = "de_thi"
    elif any(kw in duong_dan_str for kw in ['thực hành', 'thuc hanh', 'lab']):
        loai = "thuc_hanh"
    elif any(kw in duong_dan_str for kw in ['sách', 'sach', 'tham khảo']):
        loai = "sach_tham_khao"
    elif any(kw in duong_dan_str for kw in ['slide', 'lý thuyết', 'ly thuyet']):
        loai = "slide_bai_giang"

    # Tìm năm học
    nam_hoc = ""
    for part in parts:
        match = re.search(r'(\d{4}[-–]\d{4})', str(part))
        if match:
            nam_hoc = match.group(1)
            break

    return {
        "mon_hoc": mon_hoc,
        "ma_mon": ma_mon,
        "loai": loai,
        "nam_hoc": nam_hoc,
        "ten_file": duong_dan.name,
    }


def _doc_pdf(duong_dan: Path) -> str:
    """
    Đọc toàn bộ text từ file PDF.
    Trả về chuỗi text đã làm sạch, hoặc rỗng nếu lỗi.
    """
    try:
        doc = fitz.open(str(duong_dan))
        trang_texts = []
        for trang in doc:
            text = trang.get_text("text")  # type: ignore
            if text.strip():
                trang_texts.append(text)
        doc.close()
        full_text = '\n'.join(trang_texts)
        return _lam_sach_text(full_text)
    except Exception as e:
        print(f"  [SKIP] Không đọc được {duong_dan.name}: {e}")
        return ""


def duyet_pdf(thu_muc: Path = DATA_DIR) -> Generator[Path, None, None]:
    """Duyệt đệ quy để tìm tất cả file .pdf trong thư mục."""
    for item in sorted(thu_muc.rglob("*.pdf")):
        yield item


def extract_tu_file(duong_dan: Path) -> list[dict]:
    """
    Extract text từ 1 file PDF và chia thành chunks.
    Trả về list of {"id": str, "text": str, "metadata": dict}
    """
    text = _doc_pdf(duong_dan)
    if not text:
        return []

    metadata = _phan_loai_tai_lieu(duong_dan)
    chunks = _chia_chunks(text)

    ket_qua = []
    for i, chunk in enumerate(chunks):
        # ID duy nhất cho mỗi chunk
        chunk_id = f"{duong_dan.stem}__chunk{i}"
        ket_qua.append({
            "id": chunk_id,
            "text": chunk,
            "metadata": {**metadata, "chunk_index": i}
        })

    return ket_qua


def extract_tat_ca(thu_muc: Path = DATA_DIR,
                   hien_thi_tien_trinh: bool = True) -> list[dict]:
    """
    Extract text từ TOÀN BỘ PDF trong thư mục bài giảng.

    Args:
        thu_muc: Thư mục gốc chứa file PDF (mặc định: data/lectures/)
        hien_thi_tien_trinh: In tiến trình ra màn hình hay không

    Returns:
        List of chunks: [{"id": str, "text": str, "metadata": dict}, ...]
    """
    tat_ca_chunks = []
    danh_sach_pdf = list(duyet_pdf(thu_muc))

    if not danh_sach_pdf:
        print(f"[WARN] Không tìm thấy file PDF nào trong: {thu_muc}")
        return []

    print(f"[INFO] Tìm thấy {len(danh_sach_pdf)} file PDF. Bắt đầu extract...")

    for i, pdf_path in enumerate(danh_sach_pdf, 1):
        if hien_thi_tien_trinh:
            print(f"  [{i:3}/{len(danh_sach_pdf)}] {pdf_path.name[:60]}")

        chunks = extract_tu_file(pdf_path)
        tat_ca_chunks.extend(chunks)

    print(f"\n[OK] Tổng cộng: {len(tat_ca_chunks):,} chunks từ {len(danh_sach_pdf)} file PDF")
    return tat_ca_chunks
