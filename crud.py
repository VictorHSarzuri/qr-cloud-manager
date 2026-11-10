from sqlmodel import Session, select
from models import User, QRHistory
from auth import hash_password, verify_password

def authenticate_user(session: Session, username: str, password: str):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None

def register_user(session: Session, username: str, password: str):
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        return None
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def save_qr_history(session: Session, user_id: int, title: str, content: str):
    record = QRHistory(user_id=user_id, title=title, content=content)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

def get_user_history(session: Session, user_id: int):
    return session.exec(select(QRHistory).where(QRHistory.user_id == user_id).order_by(QRHistory.created_at.desc())).all()
