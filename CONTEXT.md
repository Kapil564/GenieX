# CONTEXT — GenieX

Purpose

- GenieX is an automation bot that finds today's top AI news and/or relevant GitHub commits and posts them to X (formerly Twitter). This repository is a minimal web API for commands, command registration with Telegram, and CI/CD examples.

Quick facts

- Project name: GenieX
- Runtime: Node.js (ES modules)
- Entry: `index.js`
- Key services: `services/botService.js`, `services/telegramService.js`

Environment

- Place secrets in `.env` at the project root:
  - `TELEGRAM_BOT_TOKEN=<your-telegram-token>`

Endpoints (HTTP)

- `GET /about` — metadata about the bot
- `GET /commands?cmd=/help` — returns help commands and usage
- `GET /commands?cmd=/me` — returns `whoami` information about GenieX
- `GET /commands?cmd=/rem&time=YYYY-MM-DDTHH:MM` — set a simple reminder response (demo)
- `GET /telegram/register` — register the bot commands with Telegram using `TELEGRAM_BOT_TOKEN` (calls `setMyCommands`)

Commands (registered with Telegram)

- `/me` — Describe the bot (name, purpose)
- `/help` — List available commands and short usage
- `/rem` — Demo reminder command; current API requires a `time` query param to show a confirmation

Testing & CI

- Tests use Node's built-in `node --test`; run locally with:

```powershell
npm install
npm test
```

- GitHub Actions workflow: `.github/workflows/nodejs-ci.yml` runs tests on push / pull_request.

Notes & architecture

- This repository intentionally uses a small direct HTTP client to register Telegram commands (`services/telegramService.js`) rather than a full Telegram framework (e.g., `telegraf`). That keeps the demo lightweight and focused on CI/CD examples.
- Command handling is performed in `services/botService.js` and exposed via `routes/commands.js`.

Next steps (ideas)

- Implement fetching "top 10 AI news" (RSS or news APIs) and matching logic for user profile/mood.
- Add an X posting service with OAuth or a GitHub Action that creates commits and posts content.
- Replace the direct Telegram registration with a full `telegraf` bot to handle webhook/polling and richer interactions.
- Implement a persistent reminders store and scheduled job runner (cron) to deliver `/rem` reminders.

Files of interest

- `index.js` — app bootstrap
- `routes/` — HTTP routes (`about`, `commands`, `telegram`)
- `services/` — `botService.js`, `telegramService.js`
- `.github/workflows/nodejs-ci.yml` — CI configuration
- `test/` — basic unit tests

Contact

- If you want me to implement any of the next-step items, tell me which one and I'll scaffold code and tests for it.
