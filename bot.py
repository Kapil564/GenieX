import asyncio
import logging
import os
import re
import tempfile
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from telegram import Update
from telegram.error import Conflict
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from brain import BrainStore

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Set TELEGRAM_TOKEN in your environment or .env file")

# Render / production webhook settings
PORT = int(os.getenv("PORT", "8443"))
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", f"/webhook/{TOKEN}")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

store = BrainStore()

# Try to import OpenAI Whisper for local voice transcription.
# If not installed, voice notes are saved as-is.
try:
    import whisper

    _whisper_model = whisper.load_model("base")
except Exception:
    _whisper_model = None


def _user_id(update: Update) -> int:
    return update.effective_user.id  # type: ignore[return-value]


def _short_id(ts: str) -> str:
    """Human-readable short ID based on date + counter suffix."""
    base = datetime.fromisoformat(ts).strftime("%y%m%d-%H%M")
    return f"#{base}"


def _format_note_preview(note: dict) -> str:
    lines = [f"*{_short_id(note['created_at'])}* — {note['kind'].upper()}"]
    if note.get("source_url"):
        lines.append(f"🔗 {note['source_url']}")

    body = note.get("transcript") or note.get("caption") or note.get("content") or ""
    # Truncate long bodies
    if len(body) > 240:
        body = body[:237] + "..."
    lines.append(body or "_no text_")

    if note.get("tags"):
        tag_line = " ".join(f"#{tag}" for tag in note["tags"][:8])
        lines.append(f"🏷 {tag_line}")

    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "🧠 *Welcome to GenieX — your Second Brain.*\n\n"
        "Just *send anything*: text, voice notes, photos, videos, links, or files.\n"
        "GenieX captures, tags, and indexes it so you can find it later.\n\n"
        "*Commands:*\n"
        "• /today — notes you captured today\n"
        "• /search <query> — full-text search\n"
        "• /tags — list your tags\n"
        "• /tag <tag> — notes with a specific tag\n"
        "• /random — resurface a random idea\n"
        "• /delete <id> — delete a note\n"
        "• /start — show this help"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    notes = store.today(_user_id(update))
    if not notes:
        await update.message.reply_text("Nothing captured today yet. Send something!")
        return
    await _send_notes(update, notes)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /search <keyword or phrase>")
        return
    notes = store.search(_user_id(update), query, limit=10)
    if not notes:
        await update.message.reply_text(f"No results for '{query}'.")
        return
    await _send_notes(update, notes)


async def tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tags = store.list_tags(_user_id(update))
    if not tags:
        await update.message.reply_text("No tags yet. Start dumping ideas!")
        return
    tag_list = " ".join(f"#{tag}" for tag in tags)
    await update.message.reply_text(f"🏷 Your tags:\n{tag_list}")


async def tag_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tag = " ".join(context.args).lower().lstrip("#")
    if not tag:
        await update.message.reply_text("Usage: /tag <tag>")
        return
    notes = store.list_by_tag(_user_id(update), tag, limit=10)
    if not notes:
        await update.message.reply_text(f"No notes tagged #{tag}.")
        return
    await _send_notes(update, notes)


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    note = store.random(_user_id(update))
    if not note:
        await update.message.reply_text("Your brain is empty. Time to capture something!")
        return
    await _send_note(update, note)


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args)
    if not raw:
        await update.message.reply_text("Usage: /delete <note-id>")
        return

    note_id = raw.lstrip("#")
    if note_id.isdigit():
        deleted = store.delete_note(int(note_id), _user_id(update))
    else:
        await update.message.reply_text("Use the note ID shown in previews (e.g. /delete 42).")
        return

    if deleted:
        await update.message.reply_text("Deleted. 🗑")
    else:
        await update.message.reply_text("Note not found or you don't own it.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user_id = _user_id(update)

    if message.text and message.text.startswith("/"):
        return

    # Text / link / idea
    if message.text is not None:
        url = _extract_url(message.text)
        note = store.add_note(
            user_id=user_id,
            kind="link" if url else "text",
            content=message.text,
        )
        await message.reply_text(
            f"Captured {_short_id(note['created_at'])} {'link' if url else 'note'}.\n"
            + " ".join(f"#{t}" for t in note["tags"]),
            parse_mode="Markdown",
        )
        return

    # Photo
    if message.photo:
        file_id = message.photo[-1].file_id
        note = store.add_note(
            user_id=user_id,
            kind="photo",
            content=message.caption or "",
            file_id=file_id,
            caption=message.caption,
        )
        await message.reply_text(
            f"Captured photo {_short_id(note['created_at'])}.\n"
            + " ".join(f"#{t}" for t in note["tags"]),
            parse_mode="Markdown",
        )
        return

    # Video / video note
    if message.video:
        file_id = message.video.file_id
        note = store.add_note(
            user_id=user_id,
            kind="video",
            content=message.caption or "",
            file_id=file_id,
            caption=message.caption,
        )
        await message.reply_text(
            f"Captured video {_short_id(note['created_at'])}.\n"
            + " ".join(f"#{t}" for t in note["tags"]),
            parse_mode="Markdown",
        )
        return

    # Voice note -> optional transcription
    if message.voice:
        file_id = message.voice.file_id
        transcript = None
        if _whisper_model:
            transcript = await _transcribe_voice(context, file_id)
        note = store.add_note(
            user_id=user_id,
            kind="voice",
            content="",
            file_id=file_id,
            caption=message.caption,
            transcript=transcript or "",
        )
        tags_text = " ".join(f"#{t}" for t in note["tags"])
        reply = f"Captured voice {_short_id(note['created_at'])}."
        if transcript:
            reply += f"\n📝 Transcript: {transcript[:220]}"
            if len(transcript) > 220:
                reply += "..."
        reply += f"\n{tags_text}"
        await message.reply_text(reply, parse_mode="Markdown")
        return

    # Document / file
    if message.document:
        file_id = message.document.file_id
        note = store.add_note(
            user_id=user_id,
            kind="document",
            content=message.document.file_name or "",
            file_id=file_id,
            caption=message.caption,
        )
        await message.reply_text(
            f"Captured document {_short_id(note['created_at'])}.\n"
            + " ".join(f"#{t}" for t in note["tags"]),
            parse_mode="Markdown",
        )
        return

    if message.audio:
        file_id = message.audio.file_id
        note = store.add_note(
            user_id=user_id,
            kind="audio",
            content=message.audio.file_name or "",
            file_id=file_id,
            caption=message.caption,
        )
        await message.reply_text(
            f"Captured audio {_short_id(note['created_at'])}.\n"
            + " ".join(f"#{t}" for t in note["tags"]),
            parse_mode="Markdown",
        )
        return

    await message.reply_text("Unsupported message type. Send text, voice, photo, video, audio, or document.")


async def _transcribe_voice(context: ContextTypes.DEFAULT_TYPE, file_id: str) -> Optional[str]:
    try:
        file = await context.bot.get_file(file_id)
        ext = os.path.splitext(file.file_path or "")[1] or ".oga"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_in:
            await file.download_to_drive(tmp_in.name)
            tmp_path = tmp_in.name

        result = _whisper_model.transcribe(tmp_path, fp16=False)
        os.unlink(tmp_path)
        return result.get("text", "").strip() or None
    except Exception as exc:
        logging.warning("Voice transcription failed: %s", exc)
        return None


def _extract_url(text: str) -> Optional[str]:
    match = re.search(r"https?://\S+", text)
    if not match:
        return None
    parsed = urlparse(match.group(0))
    if parsed.scheme in ("http", "https"):
        return match.group(0)
    return None


async def _send_note(update: Update, note: dict) -> None:
    text = _format_note_preview(note)
    kind = note.get("kind")
    file_id = note.get("file_id")

    if kind in ("photo", "video", "document", "audio", "voice") and file_id:
        if kind == "photo":
            await update.message.reply_photo(photo=file_id, caption=text, parse_mode="Markdown")
        elif kind == "video":
            await update.message.reply_video(video=file_id, caption=text, parse_mode="Markdown")
        elif kind == "document":
            await update.message.reply_document(document=file_id, caption=text, parse_mode="Markdown")
        elif kind == "audio":
            await update.message.reply_audio(audio=file_id, caption=text, parse_mode="Markdown")
        elif kind == "voice":
            await update.message.reply_voice(voice=file_id, caption=text, parse_mode="Markdown")
        return

    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)


async def _send_notes(update: Update, notes: list) -> None:
    # If small enough, send individually; otherwise summarize.
    if len(notes) <= 5:
        for note in notes:
            await _send_note(update, note)
        return

    lines = []
    for note in notes:
        body = note.get("transcript") or note.get("caption") or note.get("content") or ""
        body = (body[:80] + "...") if len(body) > 83 else body
        tags = " ".join(f"#{t}" for t in note["tags"][:4])
        lines.append(f"• *{note['id']}* {note['kind'].upper()}: {body} {tags}")

    text = "\n".join(lines)
    if len(text) > 3800:
        text = text[:3800] + "\n..."
    await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)


def build_application() -> Application:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("tags", tags_command))
    application.add_handler(CommandHandler("tag", tag_command))
    application.add_handler(CommandHandler("random", random_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    return application


def main() -> None:
    application = build_application()

    # Choose polling vs webhook based on environment
    webhook_url = WEBHOOK_URL or (f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}" if WEBHOOK_HOST else "")

    try:
        if webhook_url:
            logging.info("Starting webhook on %s port %s", webhook_url, PORT)
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                webhook_url=webhook_url,
                secret_token=WEBHOOK_SECRET or None,
            )
        else:
            logging.info("Starting polling mode")
            application.run_polling(allowed_updates=["message"])
    except Conflict as exc:
        logging.error("Another bot instance is already running: %s", exc)
        raise


if __name__ == "__main__":
    main()
