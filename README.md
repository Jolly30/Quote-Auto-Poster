# 🪨 Quote Auto Poster — TikTok Motivational Video Generator

Automated 24/7 pipeline that generates motivational quote videos with AI voiceover and posts them to TikTok via Buffer — entirely free, hosted on GitHub Actions.

## How It Works

```
quotes.json → random pick → edge-tts voiceover → FFmpeg overlay on stock video → upload to CDN → Buffer API → TikTok
```

## Pipeline Steps

1. **Quote selection** — picks a random entry from `quotes.json`
2. **Voice synthesis** — generates narration via Microsoft Edge TTS (`edge-tts`)
3. **Background video** — downloads a free vertical clip from Mixkit CDN (or Pexels if key provided)
4. **Background music** — optional royalty-free ambient piano from Wikimedia
5. **FFmpeg render** — overlays stylized captions on 1080×1920 video
6. **CDN upload** — hosts via GitHub Releases (public repos) or Catbox/Tmpfiles (private)
7. **Buffer post** — schedules the video on your connected TikTok account

## Live Demo

📺 **TikTok:** [@mr.cheese202](https://www.tiktok.com/@mr.cheese202)
- 32 followers, 1,678 likes
- 16+ videos posted automatically
- Daily posts via GitHub Actions → Buffer API → TikTok

## Quick Start

```bash
pip install -r requirements.txt
export BUFFER_ACCESS_TOKEN="your-buffer-token"
python video_generator.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BUFFER_ACCESS_TOKEN` | ✅ | — | Buffer API token |
| `PEXELS_API_KEY` | ❌ | — | Custom video search (uses Mixkit if absent) |
| `VOICE_SELECTOR` | ❌ | `en-GB-RyanNeural` | Edge TTS voice |
| `VOICE_RATE` | ❌ | `-8%` | Speech speed |
| `VOICE_VOLUME` | ❌ | `0.7` | Narration volume |
| `MUSIC_VOLUME` | ❌ | `0.5` | Background music volume |
| `FONT_SIZE` | ❌ | `58` | Caption font size |
| `TEXT_WRAP_WIDTH` | ❌ | `25` | Characters per line |

## 24/7 Cloud Hosting (GitHub Actions)

1. Create a **private** GitHub repo
2. Push these files: `video_generator.py`, `quotes.json`, `requirements.txt`, `.github/`
3. Add `BUFFER_ACCESS_TOKEN` to repo Secrets
4. Enable the Actions workflow — it runs daily at 9:00 AM UTC

## Output

- **Resolution:** 1080×1920 (vertical, TikTok-native)
- **Voiceover:** Neural TTS with calm documentary-style narration
- **Captions:** Auto-scaling centered white text with black border
- **Music:** Soft ambient piano (optional)

## Database

The project includes a SQLite database (`quotes.db`) for tracking:
- Quote usage (which quotes have been posted)
- Post history (timestamps, status, CDN URLs)
- Analytics (views, likes, comments, shares)

```bash
# Setup database from quotes.json
python setup_db.py

# Query via SQLite MCP or directly
sqlite3 quotes.db "SELECT * FROM quotes WHERE used_count = 0"
```

## Files

```
.
├── video_generator.py    # Main pipeline script
├── quotes.json           # 100+ curated motivational quotes
├── quotes.db             # SQLite database for tracking
├── setup_db.py           # Database setup script
├── db_utils.py           # Database helper functions
├── font.ttf              # Montserrat Bold font
├── requirements.txt      # Python dependencies
├── pitch.md              # Marp presentation slides
└── final_post.mp4        # Last generated video
```
