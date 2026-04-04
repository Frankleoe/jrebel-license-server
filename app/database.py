# -*- coding: utf-8 -*-
"""
SQLite 数据库 - 存储激活记录
"""
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "/app/data/activations.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    try:
        conn = _get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                guid TEXT,
                ip TEXT,
                product TEXT DEFAULT 'jrebel',
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS version (
                ver INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.warning(f"Database init skipped: {e}")


def record_activation(email: str, guid: str, ip: str, product: str = "jrebel"):
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO activations (email, guid, ip, product) VALUES (?, ?, ?, ?)",
            (email, guid, ip, product)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to record activation: {e}")


def get_recent_activations(limit: int = 50):
    try:
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT email, guid, ip, product, activated_at FROM activations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.warning(f"Failed to get activations: {e}")
        return []


def get_stats():
    try:
        conn = _get_conn()
        cur = conn.execute("SELECT COUNT(*) as total, COUNT(DISTINCT email) as unique_emails FROM activations")
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else {"total": 0, "unique_emails": 0}
    except Exception as e:
        logger.warning(f"Failed to get stats: {e}")
        return {"total": 0, "unique_emails": 0}
