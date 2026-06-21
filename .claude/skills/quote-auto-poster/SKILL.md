---
name: quote-auto-poster
description: Generate and post motivational quote videos to TikTok
---

# Quote Auto Poster Skill

Generate short-form motivational quote videos and schedule them to TikTok via Buffer.

## What It Does

1. Picks a random quote from `quotes.json`
2. Generates AI voiceover via `edge-tts` (Microsoft neural voices)
3. Downloads a free vertical stock video from Mixkit CDN
4. Renders a 1080×1920 video with FFmpeg — captions, voiceover, optional music
5. Uploads to a free CDN (GitHub Releases / Catbox / Tmpfiles)
6. Posts to TikTok through the Buffer scheduling API

## Commands

```bash
# Run locally (saves final_post.mp4, skips upload)
python video_generator.py

# Run with all env vars
BUFFER_ACCESS_TOKEN="token" PEXELS_API_KEY="key" python video_generator.py

# Run headless via GitHub Actions (auto-posts daily at 9:00 AM UTC)
# Just push to the repo — the .github/workflows/ handles it
```

## Key Files

- `video_generator.py` — main pipeline
- `quotes.json` — quote library (100+ entries)
- `font.ttf` — Montserrat Bold
- `requirements.txt` — `edge-tts`, `requests`

## Customization

- **Voice:** set `VOICE_SELECTOR` (e.g. `en-US-JennyNeural` for female)
- **Speed:** set `VOICE_RATE` (e.g. `-12%` for slower)
- **Font size:** set `FONT_SIZE` (default 58, auto-scales for long quotes)
- **Music:** drop a `music.mp3` or `music.ogg` in the project root
- **Videos:** set `PEXELS_API_KEY` for custom search terms
