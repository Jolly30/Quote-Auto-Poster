---
marp: true
paginate: true
transition: fade
---

<!-- slide 1 -->
# Tech Stack

- **Language:** Python 3.10+
- **TTS:** edge-tts (Microsoft neural voices, free)
- **Video:** FFmpeg (caption overlay, voice mixing)
- **Hosting:** GitHub Actions (daily cron)
- **CDN:** GitHub Releases → Catbox → Tmpfiles → Litterbox
- **Posting:** Buffer API (GraphQL + REST fallback) → TikTok
- **Database:** SQLite (quote tracking + analytics)

---

<!-- slide 2 -->
# Agents

- **Path:** `.claude/agents/quote-auto-poster.md`
- **Model:** Sonnet
- **Purpose:** Project-aware assistant that understands the full pipeline
- **Knows:** Architecture, common tasks, guardrails, config
- **Use case:** Debugging, extending features, onboarding new contributors

---

<!-- slide 3 -->
# Skills

- **Path:** `.claude/skills/quote-auto-poster/SKILL.md`
- **Purpose:** Manage quotes database and run the video pipeline
- **Database access:** SQLite MCP connected to `quotes.db`
- **Commands:** Browse quotes, add/delete quotes, check post history, check analytics, run pipeline, rebuild DB
- **Rules:** Duplicate checks before insert, confirmation before delete

---

<!-- slide 4 -->
# Methodology

- **Single-file pipeline** — `video_generator.py` does everything end-to-end
- **Database-first** — every quote tracked with `used_count`, every post logged
- **CDN fallback chain** — 4 upload targets ensure videos always go live
- **API fallback** — GraphQL first, REST second for Buffer posting
- **Zero-cost hosting** — GitHub Actions cron + free APIs only

---

<!-- slide 5 -->
# Trigger & Commands

- **Trigger:** GitHub Actions cron runs daily at 2:30 AM UTC (9:00 AM Myanmar time)
- **Manual run:** `python video_generator.py`
- **Rebuild DB:** `python setup_db.py`
- **Claude Code trigger:** Say "manage quotes" or "run the pipeline" — the skill activates automatically

---

<!-- slide 6 -->
# Summary

- 100% free, 24/7 automated TikTok content
- AI voiceover + stock footage + auto-captions
- 100+ curated quotes, never repeats until all used
- SQLite analytics for tracking performance
- One command to set up, zero maintenance after
