#!/usr/bin/env python3
"""
Setup script: converts quotes.json into a SQLite database with tables for
quotes, post history, and analytics.
"""
import json
import sqlite3
import os
from datetime import datetime

DB_PATH = "quotes.db"
JSON_PATH = "quotes.json"

def setup_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Quotes table ──
    cur.execute("""
        CREATE TABLE quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            author TEXT DEFAULT 'Did you know?',
            category TEXT DEFAULT 'general',
            used_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Post history table ──
    cur.execute("""
        CREATE TABLE post_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER NOT NULL,
            posted_at TEXT DEFAULT (datetime('now')),
            platform TEXT DEFAULT 'tiktok',
            video_path TEXT,
            cdn_url TEXT,
            buffer_post_id TEXT,
            status TEXT DEFAULT 'scheduled',
            FOREIGN KEY (quote_id) REFERENCES quotes(id)
        )
    """)

    # ── Analytics table ──
    cur.execute("""
        CREATE TABLE analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            recorded_at TEXT DEFAULT (datetime('now')),
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            watch_time_sec REAL DEFAULT 0,
            FOREIGN KEY (post_id) REFERENCES post_history(id)
        )
    """)

    # ── Indexes for fast queries ──
    cur.execute("CREATE INDEX idx_quotes_used ON quotes(used_count)")
    cur.execute("CREATE INDEX idx_posts_date ON post_history(posted_at)")
    cur.execute("CREATE INDEX idx_posts_status ON post_history(status)")
    cur.execute("CREATE INDEX idx_analytics_post ON analytics(post_id)")

    # ── Load quotes from JSON ──
    with open(JSON_PATH, "r") as f:
        quotes = json.load(f)

    for q in quotes:
        cur.execute(
            "INSERT INTO quotes (quote, author) VALUES (?, ?)",
            (q["quote"], q.get("author", "Did you know?"))
        )

    conn.commit()
    print(f"Loaded {len(quotes)} quotes into {DB_PATH}")

    # ── Verify ──
    cur.execute("SELECT COUNT(*) FROM quotes")
    count = cur.fetchone()[0]
    print(f"Quotes in database: {count}")

    cur.execute("SELECT id, quote, used_count FROM quotes LIMIT 3")
    print("\nSample rows:")
    for row in cur.fetchall():
        print(f"  [{row[0]}] {row[1][:60]}... (used {row[2]}x)")

    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")

if __name__ == "__main__":
    setup_database()
