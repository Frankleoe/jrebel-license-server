# -*- coding: utf-8 -*-
"""
SQLite 数据库 - 存储激活记录
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "/app/activations.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
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


def record_activation(email: str, guid: str, ip: str, product: str = "jrebel"):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO activations (email, guid, ip, product) VALUES (?, ?, ?, ?)",
        (email, guid, ip, product)
    )
    conn.commit()
    conn.close()


def get_recent_activations(limit: int = 50):
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT email, guid, ip, product, activated_at FROM activations ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    conn = _get_conn()
    cur = conn.execute("SELECT COUNT(*) as total, COUNT(DISTINCT email) as unique_emails FROM activations")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "unique_emails": 0}
