---
name: quote-auto-poster
model: sonnet
description: Agent for maintaining and extending the TikTok quote video auto-poster
---

# Quote Auto Poster Agent

You are working on a TikTok motivational quote video auto-poster pipeline.

## Project Context

- **Language:** Python 3.10+
- **Core deps:** `edge-tts` (neural TTS), `requests`, `ffmpeg` (system)
- **Hosting:** GitHub Actions (daily cron), free Mixkit CDN, GitHub Releases
- **Posting:** Buffer API (GraphQL + REST fallback) → TikTok

## Architecture

```
quotes.json ─→ video_generator.py ─→ FFmpeg ─→ final_post.mp4
                    │                                   │
                    ├─ edge-tts (voiceover)              ├─ CDN upload
                    ├─ Mixkit/Pexels (background)        └─ Buffer → TikTok
                    └─ Wikimedia (music)
```

## Key Behaviors

- The script is a single-file pipeline (`video_generator.py`) — no frameworks
- Text captions are rendered via FFmpeg `drawtext` filter with auto-scaling font size
- Voiceover is synthesized asynchronously via `edge-tts.Communicate`
- Music mixing uses FFmpeg `amix` filter (voice + bgm)
- CDN upload order: GitHub Releases (public repos) → Catbox → Tmpfiles → Litterbox
- Buffer posting tries GraphQL API first, falls back to legacy REST

## Common Tasks

- Adding new quotes: edit `quotes.json` (array of `{quote, author}`)
- Changing voice: update `VOICE_SELECTOR` env var
- Debugging FFmpeg: check `final_post.mp4` output, enable verbose with `-v verbose`
- Adding new video sources: append URLs to `DIRECT_VIDEO_URLS` list
- Music: drop `music.mp3`/`music.ogg` in root to override auto-download

## Guardrails

- Never commit API tokens — use GitHub Secrets or env vars
- Always test FFmpeg commands locally before pushing workflow changes
- Keep the pipeline single-file unless it exceeds ~1000 lines
