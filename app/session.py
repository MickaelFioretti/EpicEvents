from contextlib import contextmanager
from typing import Generator
from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://postgres:password@db/epic_events"

engine = create_engine(DATABASE_URL, echo=False)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
