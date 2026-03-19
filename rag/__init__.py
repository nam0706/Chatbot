"""
rag/ - Module RAG (Retrieval-Augmented Generation) cho ITBot
Gồm 3 thành phần:
  - extract_pdf.py  : Đọc PDF → text chunks
  - indexer.py      : Tạo ChromaDB vector index (chạy 1 lần)
  - retriever.py    : Tìm kiếm ngữ nghĩa theo câu hỏi
"""
