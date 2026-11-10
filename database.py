import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:pass@localhost:5432/qr_db"
)

# Render / Supabase / Neon require SSL connection
engine = create_engine(DATABASE_URL, echo=True, connect_args={"sslmode": "require"} if "postgresql" in DATABASE_URL else {})

def get_session():
    with Session(engine) as session:
        yield session
