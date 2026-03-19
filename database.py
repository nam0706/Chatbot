"""
database.py - Quản lý SQLite Database bằng SQLAlchemy.
Lưu trữ thông tin người dùng và lịch sử trò chuyện.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from pathlib import Path

# Cấu hình đường dẫn DB
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "chatbot.db"

# Khởi tạo SQLAlchemy
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Định nghĩa Models --------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ với bảng tin nhắn
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    role = Column(String, nullable=False)  # 'user' hoặc 'model'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")


# Khởi tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)


# --- Hàm tương tác Database ---------------------------------------------------

def get_or_create_user(email: str, name: str, avatar_url: str = "") -> User:
    """Tạo user mới nếu chưa tồn tại; cập nhật name và avatar nếu đã có."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name, avatar_url=avatar_url)
            db.add(user)
        else:
            # Cập nhật thông tin mới nhất mỗi lần đăng nhập
            user.name = name
            user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def add_message(email: str, role: str, content: str):
    """Thêm một tin nhắn mới vào lịch sử của người dùng."""
    db = SessionLocal()
    try:
        message = Message(user_email=email, role=role, content=content)
        db.add(message)
        db.commit()
    finally:
        db.close()


def get_user_history(email: str) -> list[dict]:
    """Lấy danh sách tin nhắn theo thứ tự thời gian của user."""
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(Message.user_email == email).order_by(Message.timestamp.asc()).all()
        # Chuyển đổi sang format dict giống với session_state.lich_su
        history = []
        for msg in messages:
            history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
        return history
    finally:
        db.close()

def get_display_history(email: str) -> list[dict]:
    """Lấy danh sách tin nhắn để hiển thị UI (role: assistant/user, content)."""
    db = SessionLocal()
    try:
        messages = db.query(Message).filter(Message.user_email == email).order_by(Message.timestamp.asc()).all()
        display_hist = []
        for msg in messages:
            role = "user" if msg.role == "user" else "assistant"
            display_hist.append({
                "role": role,
                "content": msg.content
            })
        return display_hist
    finally:
        db.close()
