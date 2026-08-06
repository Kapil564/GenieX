# Telegram Storage Bot

This project creates a Telegram bot that stores text, photos, and videos locally and lets you retrieve them later.

## Features

- Save text messages
- Save photos and videos
- Retrieve items by name or ID
- List all saved items

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a Telegram bot with BotFather and copy its token.
3. Create a `.env` file from `.env.example` and set your token:
   ```bash
   copy .env.example .env
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

- `/start` - show help
- `/save <name>` - prepare the next message/media to store
- `/list` - list saved items
- `/get <name-or-id>` - retrieve a stored item
