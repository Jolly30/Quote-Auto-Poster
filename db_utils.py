#!/usr/bin/env python3
"""
Database utilities for Quote Auto Poster.
Tracks quote usage, post history, and analytics in quotes.db.
"""
import sqlite3
from datetime import datetime

DB_PATH = "quotes.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_least_used_quote():
    """Pick a quote that hasn't been posted yet, or the least used one."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, quote, author FROM quotes
        ORDER BY used_count ASC, RANDOM()
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "quote": row[1], "author": row[2]}
    return None

def mark_quote_used(quote_id):
    """Increment the used_count for a quote."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE quotes SET used_count = used_count + 1 WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()

def record_post(quote_id, video_path=None, cdn_url=None, buffer_post_id=None, status="scheduled"):
    """Insert a row into post_history and return its id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO post_history (quote_id, video_path, cdn_url, buffer_post_id, status)
        VALUES (?, ?, ?, ?, ?)
    """, (quote_id, video_path, cdn_url, buffer_post_id, status))
    post_id = cur.lastrowid
    conn.commit()
    conn.close()
    return post_id

def update_post_status(post_id, status, cdn_url=None):
    """Update a post's status (and optionally cdn_url)."""
    conn = get_connection()
    cur = conn.cursor()
    if cdn_url:
        cur.execute("UPDATE post_history SET status = ?, cdn_url = ? WHERE id = ?", (status, cdn_url, post_id))
    else:
        cur.execute("UPDATE post_history SET status = ? WHERE id = ?", (status, post_id))
    conn.commit()
    conn.close()

def record_analytics(post_id, views=0, likes=0, comments=0, shares=0, watch_time=0):
    """Store a snapshot of post performance."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analytics (post_id, views, likes, comments, shares, watch_time_sec)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (post_id, views, likes, comments, shares, watch_time))
    conn.commit()
    conn.close()

def get_stats():
    """Return a summary dict of all-time stats."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM quotes")
    total_quotes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM quotes WHERE used_count > 0")
    used_quotes = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM post_history")
    total_posts = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM post_history WHERE status = 'posted'")
    successful_posts = cur.fetchone()[0]

    cur.execute("SELECT SUM(views), SUM(likes), SUM(comments), SUM(shares) FROM analytics")
    row = cur.fetchone()
    total_views = row[0] or 0
    total_likes = row[1] or 0
    total_comments = row[2] or 0
    total_shares = row[3] or 0

    conn.close()
    return {
        "total_quotes": total_quotes,
        "used_quotes": used_quotes,
        "unused_quotes": total_quotes - used_quotes,
        "total_posts": total_posts,
        "successful_posts": successful_posts,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
    }
