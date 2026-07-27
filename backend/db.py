from pathlib import Path

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from backend.config import settings

if settings.database_url.startswith("sqlite:///./"):
    db_path = Path(settings.database_url.removeprefix("sqlite:///./"))
    db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
