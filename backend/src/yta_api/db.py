from typing import Generator
from sqlalchemy.orm import Session
from yta_core.db.session import SessionFactory


def get_database_session() -> Generator[Session, None, None]:
    database_session = SessionFactory()
    try:
        yield database_session
    finally:
        database_session.close()
