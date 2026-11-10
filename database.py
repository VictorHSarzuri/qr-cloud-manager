import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:pass@localhost:5432/qr_db"
)

# Forzamos connect_args para asegurar compatibilidad de red y SSL
engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    connect_args={"sslmode": "require"}
)

def get_session():
    with Session(engine) as session:
        yield session