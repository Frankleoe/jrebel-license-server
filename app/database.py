# -*- coding: utf-8 -*-
"""
数据库层 - 支持 MySQL 和 SQLite
通过环境变量选择：MYSQL_URL 则用 MySQL，否则用 SQLite
"""
import os
import logging

logger = logging.getLogger(__name__)

_use_sqlite = True
_engine = None

try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.pool import QueuePool

    Base = declarative_base()

    class Activation(Base):
        __tablename__ = "activations"
        id = Column(Integer, primary_key=True, autoincrement=True)
        email = Column(String(255))
        guid = Column(String(255))
        ip = Column(String(45))
        product = Column(String(64), default="jrebel")
        activated_at = Column(DateTime, default=text("CURRENT_TIMESTAMP"))

    _mysql_url = os.getenv("MYSQL_URL", "").strip()
    if _mysql_url:
        _engine = create_engine(
            _mysql_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        _use_sqlite = False
        logger.info(f"MySQL connected: {_engine.url.host}")
    else:
        import sqlite3
        _sqlite_path = os.getenv("DB_PATH", "/app/data/activations.db")
        _db_dir = os.path.dirname(_sqlite_path)
        if _db_dir:
            os.makedirs(_db_dir, exist_ok=True)
        _engine = create_engine(f"sqlite:///{_sqlite_path}", connect_args={"check_same_thread": False})
        logger.info(f"SQLite: {_sqlite_path}")

    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine)

except ImportError:
    _engine = None


def _session():
    if _engine is None:
        return None
    return _Session()


def record_activation(email: str, guid: str, ip: str, product: str = "jrebel"):
    if _engine is None:
        return
    sess = _session()
    if sess is None:
        return
    try:
        from sqlalchemy import text
        if _use_sqlite:
            sess.execute(
                text("INSERT INTO activations (email, guid, ip, product) VALUES (:e, :g, :i, :p)"),
                {"e": email, "g": guid, "i": ip, "p": product}
            )
        else:
            sess.add(Activation(email=email, guid=guid, ip=ip, product=product))
        sess.commit()
    except Exception as ex:
        logger.warning(f"record_activation failed: {ex}")
        sess.rollback()
    finally:
        sess.close()


def get_recent_activations(limit: int = 100):
    if _engine is None:
        return []
    sess = _session()
    if sess is None:
        return []
    try:
        from sqlalchemy import text
        rows = sess.execute(
            text("SELECT email, guid, ip, product, activated_at FROM activations ORDER BY id DESC LIMIT :l"),
            {"l": limit}
        ).fetchall()
        return [dict(r._mapping) for r in rows]
    except Exception as ex:
        logger.warning(f"get_recent_activations failed: {ex}")
        return []
    finally:
        sess.close()


def get_stats():
    if _engine is None:
        return {"total": 0, "unique_emails": 0}
    sess = _session()
    if sess is None:
        return {"total": 0, "unique_emails": 0}
    try:
        from sqlalchemy import text
        row = sess.execute(
            text("SELECT COUNT(*) as total, COUNT(DISTINCT email) as unique_emails FROM activations")
        ).fetchone()
        return {"total": row[0], "unique_emails": row[1]} if row else {"total": 0, "unique_emails": 0}
    except Exception as ex:
        logger.warning(f"get_stats failed: {ex}")
        return {"total": 0, "unique_emails": 0}
    finally:
        sess.close()
