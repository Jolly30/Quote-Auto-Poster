---
name: quote-auto-poster
description: Manage the quotes database and video posting pipeline
---

# Quote Auto Poster Skill

Your job is to manage the quotes database (`quotes.db`) and help run the TikTok video posting pipeline.

## Database Access

You have access to the SQLite MCP connected to `quotes.db`. Use it for all database operations. The database has three tables:

- **quotes** — id, quote, author, category, used_count
- **post_history** — quote_id, posted_at, platform, video_path, cdn_url, status
- **analytics** — post_id, views, likes, comments, shares, watch_time_sec

## When the user asks to...

### Find or browse quotes
Query the `quotes` table. Examples:
- "show me quotes" → `SELECT id, quote, used_count FROM quotes`
- "unused quotes" → `SELECT * FROM quotes WHERE used_count = 0`
- "most posted quotes" → `SELECT * FROM quotes ORDER BY used_count DESC LIMIT 10`

### Add a new quote
1. First check for duplicates: `SELECT * FROM quotes WHERE quote LIKE '%keywords%'`
2. Only insert if no match found: `INSERT INTO quotes (quote, author) VALUES (?, ?)`
3. Confirm what was added

### Delete a quote
1. Show the quote first so the user can confirm
2. Also delete related post_history and analytics rows (foreign key)

### Check post history
Query `post_history` joined with `quotes`:
```sql
SELECT p.id, q.quote, p.posted_at, p.status, p.cdn_url
FROM post_history p JOIN quotes q ON p.quote_id = q.id
ORDER BY p.posted_at DESC
```

### Check analytics / performance
Query the `analytics` table joined with post_history:
```sql
SELECT q.quote, SUM(a.views) as total_views, SUM(a.likes) as total_likes
FROM analytics a
JOIN post_history p ON a.post_id = p.id
JOIN quotes q ON p.quote_id = q.id
GROUP BY q.id ORDER BY total_views DESC
```

### Run the pipeline
```bash
python video_generator.py
```
This picks the least-used quote, generates a video, and posts to TikTok via Buffer.

### Reset or rebuild the database
```bash
python setup_db.py
```
This drops and recreates `quotes.db` from `quotes.json`.

## Rules
- Always check for duplicates before inserting quotes
- Never delete quotes without user confirmation
- Use `used_count` to track which quotes have been posted
- The pipeline (`video_generator.py`) calls `db_utils.py` to auto-track posts
