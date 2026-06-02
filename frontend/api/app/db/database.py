from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from app.core.config import settings
from typing import Generator
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.sync_database_url,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if settings.USE_SQLITE else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized: {settings.sync_database_url}")


def close_db():
    engine.dispose()
