# 🧠 GenieX — Telegram Second Brain

A personal Telegram bot that captures your ideas, links, voice notes, photos, videos, and files, then makes them searchable and resurfaceable.

Most ideas die because capturing them is too slow. GenieX turns your Telegram into a zero-friction second brain: just forward or send anything, and the bot tags, indexes, and stores it.

---

## Features

- **Text, links, photos, videos, voice notes, audio, documents** — capture anything.
- **Auto-tagging** with `#hashtags` and keyword inference (`idea`, `todo`, `read-later`, `work`, etc.).
- **Full-text search** via SQLite FTS5.
- **Voice transcription** using OpenAI Whisper (optional, local).
- **Resurface ideas** with `/random`.
- **Browse by tag** with `/tags` and `/tag <tag>`.
- **Daily recap** with `/today`.
- **Delete** items with `/delete <id>`.

---

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Show help |
| `/today` | Notes captured today |
| `/search <query>` | Full-text search |
| `/tags` | List all your tags |
| `/tag <tag>` | Show notes with a tag |
| `/random` | Resurface a random note |
| `/delete <id>` | Delete a note by ID |

Just **send a message normally** — the bot auto-captures it.

---

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   > Voice transcription requires `openai-whisper`, which also needs `ffmpeg` installed on your system.

2. Create a Telegram bot with [@BotFather](https://t.me/botfather) and copy the token.

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then paste your token:
   ```bash
   TELEGRAM_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

---

## Deploy on Render (Free Tier)

Render's free web services spin down after inactivity. **Polling bots die** because the long-running connection is dropped. Use **webhooks** instead: Telegram calls your Render URL whenever someone messages the bot, and Render wakes the service to handle it.

### 1. Create a Render Web Service

1. Push this repo to GitHub (already done).
2. Go to [render.com](https://render.com) → **New +** → **Web Service**.
3. Connect your GitHub repository (`Kapil564/GenieX`).
4. Use these settings:

| Field | Value |
|-------|-------|
| **Name** | `geniex-bot` (or anything) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python bot.py` |
| **Plan** | Free |

### 2. Set Environment Variables

In Render → your service → **Environment** → add:

| Key | Value |
|-----|-------|
| `TELEGRAM_TOKEN` | Your bot token from @BotFather |
| `WEBHOOK_HOST` | `https://geniex-bot-xxx.onrender.com` (your Render URL) |
| `WEBHOOK_SECRET` | A random secret string (optional but recommended) |

You can leave `PORT` blank — Render sets it automatically.

The bot will detect `WEBHOOK_HOST` and switch to webhook mode automatically.

### 3. Set Telegram Webhook

After the service is live, run this once to tell Telegram where to send updates:

```bash
BOT_TOKEN="your_bot_token"
WEBHOOK_URL="https://geniex-bot-xxx.onrender.com/webhook/$BOT_TOKEN"

curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$WEBHOOK_URL\"}"
```

To verify:

```bash
curl "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"
```

### 4. Switch Back to Polling (Local Dev)

Just unset `WEBHOOK_HOST` and run `python bot.py`. The bot falls back to polling.

To delete the webhook manually:

```bash
curl "https://api.telegram.org/bot<token>/deleteWebhook"
```

---

## How It Works

1. **Capture** — You send a message to the bot.
2. **Extract** — Links, hashtags, and content are parsed.
3. **Transcribe** — Voice notes are converted to text with Whisper (if available).
4. **Tag** — Automatic tags are added from `#hashtags` and keywords.
5. **Index** — Everything goes into a local SQLite database with FTS5 search.
6. **Retrieve** — Search, browse tags, or get a random spark later.

---

## Storage

- All data lives in `data/brain.db` (SQLite).
- Voice transcription is handled locally by Whisper — no cloud API call.
- Media files themselves are stored as Telegram file IDs, not downloaded locally (which keeps storage small and retrieval fast).

> ⚠️ On Render free tier, the filesystem is ephemeral. If the service restarts, `data/brain.db` is lost. For persistence, consider:
> - Mounting a [Render Disk](https://render.com/docs/disks) (paid)
> - Switching to a hosted database like [Supabase Postgres](https://supabase.com) or [SQLite on Turso](https://turso.tech)

---

## Optional: Disable Voice Transcription

If you don’t want to install Whisper/ffmpeg, remove or comment `openai-whisper` in `requirements.txt`. The bot will still save voice notes and send them back on request, it just won’t transcribe them.

---

## File Structure

```
GenieX/
├── bot.py            # Telegram bot handlers and logic
├── brain.py          # SQLite storage, tagging, search
├── requirements.txt  # Python dependencies
├── .env.example      # Environment template
├── .gitignore        # Ignores database / env files
├── data/             # SQLite database directory
└── readme.md         # This file
```

---

## Future Ideas

- [ ] Weekly email/Summary digest
- [ ] `/summary` to auto-summarize long notes with an LLM
- [ ] Export to Markdown / Notion / Obsidian
- [ ] Scheduled reminders (e.g. "show me ideas from 30 days ago")
- [ ] Web dashboard for browsing captured notes
- [ ] Chrome extension to send links directly to the bot

---

## License

MIT

Built by **Kapil Sisodiya**.
