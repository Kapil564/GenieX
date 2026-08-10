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

## Setup

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
   ```
   TELEGRAM_TOKEN=your_bot_token_here
   ```

4. Run the bot:
   ```bash
   python bot.py
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
