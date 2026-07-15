# 🎬 Quote Auto Poster

> Fully automated TikTok video generator — picks motivational quotes, generates AI voiceover, renders captions on cinematic stock footage, and posts daily via Buffer. **100% free, zero maintenance.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![TikTok](https://img.shields.io/badge/TikTok-@mr.cheese202-black?logo=tiktok)](https://www.tiktok.com/@mr.cheese202)

## How It Works

```
quotes.json → random pick → edge-tts voiceover → FFmpeg overlay on stock video → upload to CDN → Buffer API → TikTok
```

One script. One cron job. Daily motivational content — forever.

## Pipeline Steps

| Step | What happens |
|------|-------------|
| 1. **Quote selection** | Picks a random entry from `quotes.json` (100+ curated quotes, no repeats until all used) |
| 2. **Voice synthesis** | Generates narration via Microsoft Edge TTS — calm, documentary-style neural voice |
| 3. **Background video** | Downloads a free vertical clip from Mixkit CDN (or Pexels if key provided) |
| 4. **Background music** | Soft ambient piano from Wikimedia Commons (royalty-free) |
| 5. **FFmpeg render** | Overlays auto-scaling centered white captions on 1080×1920 video |
| 6. **CDN upload** | Hosts via GitHub Releases (public) or Catbox/Tmpfiles (private) |
| 7. **Buffer post** | Schedules the video on your connected TikTok account |

## Live Demo

📺 **TikTok:** [@mr.cheese202](https://www.tiktok.com/@mr.cheese202)

- 32 followers, 1,678+ likes
- 16+ videos posted automatically
- Daily posts via GitHub Actions → Buffer API → TikTok

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Jolly30/Quote-Auto-Poster.git
cd Quote-Auto-Poster

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Buffer token
export BUFFER_ACCESS_TOKEN="your-buffer-token"

# 4. Run the pipeline
python video_generator.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `BUFFER_ACCESS_TOKEN` | ✅ | — | Buffer API token for TikTok posting |
| `PEXELS_API_KEY` | ❌ | — | Custom video search (uses free Mixkit if absent) |
| `VOICE_SELECTOR` | ❌ | `en-GB-RyanNeural` | Edge TTS voice (see options below) |
| `VOICE_RATE` | ❌ | `-8%` | Speech speed adjustment |
| `VOICE_VOLUME` | ❌ | `0.7` | Narration volume (0.0–1.0) |
| `MUSIC_VOLUME` | ❌ | `0.5` | Background music volume |
| `FONT_SIZE` | ❌ | `58` | Caption font size |
| `TEXT_WRAP_WIDTH` | ❌ | `25` | Characters per line before wrapping |

### Available Voices

| Voice ID | Style |
|----------|-------|
| `en-GB-RyanNeural` | British Male — Calm, deep, documentary narrator (**default**) |
| `en-US-BrianNeural` | American Male — Warm, sincere, conversational |
| `en-US-JennyNeural` | American Female — Soft, comforting |
| `en-US-AvaNeural` | American Female — Warm, expressive |
| `en-GB-SoniaNeural` | British Female — Soothing, sophisticated |

## 24/7 Cloud Hosting (GitHub Actions)

The pipeline runs automatically every day at **9:00 AM Myanmar time** (2:30 AM UTC) via GitHub Actions.

### Setup

1. Create a **GitHub repo** (public or private)
2. Push: `video_generator.py`, `quotes.json`, `requirements.txt`, `.github/`
3. Add `BUFFER_ACCESS_TOKEN` to **Repository Secrets**
4. Enable the Actions workflow — it runs daily on cron

### Manual Trigger

You can also trigger a run manually from the **Actions** tab → "Run workflow".

## Output Specs

| Property | Value |
|----------|-------|
| Resolution | 1080×1920 (vertical, TikTok-native) |
| Voiceover | Neural TTS with calm documentary-style narration |
| Captions | Auto-scaling centered white text with black border |
| Music | Soft ambient piano (Gymnopédie No. 1 & No. 2) |
| File size | ~2 MB per video |

## Database

SQLite database (`quotes.db`) tracks everything:

- **quotes** — 100+ curated quotes with usage counts
- **post_history** — every post with status, CDN URL, and Buffer post ID
- **analytics** — engagement metrics (views, likes, comments, shares)

```bash
# Setup database from quotes.json
python setup_db.py

# Query directly
sqlite3 quotes.db "SELECT quote, author FROM quotes WHERE used_count = 0 LIMIT 5"
sqlite3 quotes.db "SELECT * FROM post_history ORDER BY created_at DESC LIMIT 10"
```

## Claude Code Integration

This project includes custom Claude Code tooling:

- **MCP Server** — SQLite connection to `quotes.db` for browsing, querying, and managing quotes
- **Skill** — Manages the quotes database and runs the pipeline via natural language
- **Agent** — Project-aware assistant with full pipeline knowledge for debugging and extending

## Project Structure

```
├── video_generator.py    # Main pipeline script
├── quotes.json           # 100+ curated motivational quotes
├── quotes.db             # SQLite database for tracking
├── setup_db.py           # Database setup script
├── db_utils.py           # Database helper functions
├── font.ttf              # Montserrat Bold font
├── requirements.txt      # Python dependencies
├── pitch.md              # Marp presentation slides
├── final_post.mp4        # Last generated video
├── screenshots/          # Project screenshots
├── slides/               # Presentation slides
├── .github/workflows/    # GitHub Actions cron job
├── .claude/              # Claude Code agents & skills
└── .mcp.json             # MCP server configuration
```

## License

MIT — use it, fork it, automate your own content.
