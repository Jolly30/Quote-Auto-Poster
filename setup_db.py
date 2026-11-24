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

    total_loaded = 0
    categories = ["romance", "sad", "motivate", "motivation", "neutral"]

    # ── 1. Check & load quotes from category JSON & text files ──
    # Supports e.g. neutral.json, romance.json, sad.json, motivate.json
    # or romance.txt, sad.txt, etc.
    found_category_files = False
    for cat in categories:
        # Check JSON files
        possible_json_files = [
            f"{cat}.json",
            f"{cat}_quotes.json",
            f"quotes_{cat}.json",
            os.path.join(cat, "quotes.json"),
            os.path.join(cat, f"{cat}.json")
        ]
        for pf in possible_json_files:
            if os.path.exists(pf):
                found_category_files = True
                print(f"Loading quotes from JSON file: {pf} (category: {cat})")
                with open(pf, "r", encoding="utf-8") as jf:
                    data = json.load(jf)
                    items = data if isinstance(data, list) else data.get("quotes", [])
                    for item in items:
                        if isinstance(item, dict):
                            text = item.get("quote", "").strip()
                            author = item.get("author", "")
                        else:
                            text = str(item).strip()
                            author = ""
                        if text:
                            cur.execute(
                                "INSERT INTO quotes (quote, author, category) VALUES (?, ?, ?)",
                                (text, author, cat)
                            )
                            total_loaded += 1

        # Check text files
        possible_txt_files = [
            f"{cat}.txt",
            f"{cat}_quotes.txt",
            f"quotes_{cat}.txt",
            os.path.join(cat, "quotes.txt"),
            os.path.join(cat, f"{cat}.txt")
        ]
        for pf in possible_txt_files:
            if os.path.exists(pf):
                found_category_files = True
                print(f"Loading quotes from text file: {pf} (category: {cat})")
                with open(pf, "r", encoding="utf-8") as tf:
                    for line in tf:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            cur.execute(
                                "INSERT INTO quotes (quote, author, category) VALUES (?, ?, ?)",
                                (line, "", cat)
                            )
                            total_loaded += 1

    # ── 2. Fall back to quotes.json only if no category files were found ──
    if not found_category_files and os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            quotes_data = json.load(f)

        if isinstance(quotes_data, list):
            for q in quotes_data:
                cur.execute(
                    "INSERT INTO quotes (quote, author, category) VALUES (?, ?, ?)",
                    (q["quote"], q.get("author", ""), q.get("category", "general"))
                )
                total_loaded += 1
        elif isinstance(quotes_data, dict):
            for cat, items in quotes_data.items():
                for item in items:
                    if isinstance(item, str):
                        cur.execute(
                            "INSERT INTO quotes (quote, author, category) VALUES (?, ?, ?)",
                            (item.strip(), "", cat)
                        )
                    elif isinstance(item, dict):
                        cur.execute(
                            "INSERT INTO quotes (quote, author, category) VALUES (?, ?, ?)",
                            (item.get("quote", "").strip(), item.get("author", ""), cat)
                        )
                    total_loaded += 1

    conn.commit()
    print(f"Loaded {total_loaded} total quotes into {DB_PATH}")

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
