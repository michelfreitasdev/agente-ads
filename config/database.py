import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


def _build_database_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_name = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB")
    db_user = os.getenv("DB_USER") or os.getenv("POSTGRES_USER")
    db_password = os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    if not all([db_name, db_user, db_password]):
        return None

    return f"postgresql://{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = _build_database_url()
if not DATABASE_URL:
    raise RuntimeError(
        "Configuração de banco ausente. Defina DATABASE_URL ou DB_NAME/DB_USER/DB_PASSWORD."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gerador de sessão do banco — usado como dependência no FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
