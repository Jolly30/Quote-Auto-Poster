---
marp: true
paginate: true
transition: fade
# PechaKucha: 6 slides, 20s auto-advance. Do not change the count.
auto-advance: 20
---

<!-- slide 1 -->
# Who's my person?
Content creators who want to grow on TikTok with motivational content — but don't have time to edit videos, record voiceovers, or post every day manually.
<!-- 20s -->

---

<!-- slide 2 -->
# Their problem
Posting consistently on TikTok is exhausting. Hiring editors is expensive. Most automation tools cost $50+/month or break after a week. They need a **free, 24/7, zero-maintenance** pipeline.

---

<!-- slide 3 -->
# What I built
**Quote Auto Poster** — a fully automated TikTok video generator that:
- Picks a random motivational quote
- Generates a neural AI voiceover
- Overlays captions on cinematic stock footage
- Posts to TikTok daily via Buffer — all for $0/month

---

<!-- slide 4 -->
# How I built it
- **MCP**: Playwright (browser automation) + Context7 (up-to-date docs)
- **Skill**: quote-auto-poster — generate & schedule video posts
- **Agent**: project-aware assistant with full pipeline knowledge
- **Core stack**: Python, edge-tts, FFmpeg, GitHub Actions, Buffer API

---

<!-- slide 5 -->
# Why it matters
- **100% free** — no paid hosting, no paid APIs, no n8n
- **Runs 24/7** — GitHub Actions cron, daily at 9 AM UTC
- **Zero code required** — set up in under 5 minutes
- **Fresh content** — 100+ curated quotes, random stock videos, neural voice

---

<!-- slide 6 -->
# Done checklist
- [x] repo public
- [x] MCP + skill + agent used
- [x] report.md in team repo
- [x] README.md with setup guide
- [x] .mcp.json configured
- [x] .claude/skills + .claude/agents created
