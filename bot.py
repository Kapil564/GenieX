import logging
import os
from typing import Optional

from dotenv import load_dotenv
from telegram.error import Conflict
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from storage import Storage

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Set TELEGRAM_TOKEN in your environment or .env file")

storage = Storage()


async def start(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Welcome to your personal Telegram storage bot.\n\n"
        "Commands:\n"
        "- /save <name> - prepare the next message/media to be stored under a name\n"
        "- /list - show all saved items\n"
        "- /get <name-or-id> - retrieve a stored item\n"
        "- /start - show this help\n\n"
        "You can store text, photos, videos, documents, audio, and voice notes."
    )
    await update.message.reply_text(help_text)


async def save_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /save <name>")
        return

    name = " ".join(context.args)
    context.user_data["pending_name"] = name
    await update.message.reply_text(f"Next message will be saved as '{name}'.")


async def list_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = storage.list_items()
    if not items:
        await update.message.reply_text("No items stored yet.")
        return

    lines = [f"{item['id']} - {item['name']} ({item['type']})" for item in items]
    await update.message.reply_text("Saved items:\n" + "\n".join(lines))


async def get_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /get <name-or-id>")
        return

    lookup = " ".join(context.args)
    item = storage.get_item(lookup)
    if not item:
        await update.message.reply_text(f"No item found for '{lookup}'.")
        return

    kind = item["type"]
    if kind == "text":
        await update.message.reply_text(item["value"])
    elif kind == "photo":
        await update.message.reply_photo(photo=item["file_id"], caption=item.get("caption") or "")
    elif kind == "video":
        await update.message.reply_video(video=item["file_id"], caption=item.get("caption") or "")
    elif kind == "document":
        await update.message.reply_document(document=item["file_id"], caption=item.get("caption") or "")
    elif kind == "audio":
        await update.message.reply_audio(audio=item["file_id"], caption=item.get("caption") or "")
    elif kind == "voice":
        await update.message.reply_voice(voice=item["file_id"], caption=item.get("caption") or "")
    else:
        await update.message.reply_text("This item type cannot be retrieved yet.")


async def handle_message(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text and update.message.text.startswith("/"):
        return

    message = update.message
    pending_name: Optional[str] = context.user_data.pop("pending_name", None)
    name = pending_name or f"item-{len(storage.list_items()) + 1}"

    if message.text is not None:
        storage.add_item(name, "text", message.text)
        await message.reply_text(f"Saved as '{name}'.")
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        storage.add_item(name, "photo", message.caption or "", file_id=file_id, caption=message.caption)
        await message.reply_text(f"Photo saved as '{name}'.")
        return

    if message.video:
        file_id = message.video.file_id
        storage.add_item(name, "video", message.caption or "", file_id=file_id, caption=message.caption)
        await message.reply_text(f"Video saved as '{name}'.")
        return

    if message.document:
        file_id = message.document.file_id
        storage.add_item(name, "document", message.caption or "", file_id=file_id, caption=message.caption)
        await message.reply_text(f"Document saved as '{name}'.")
        return

    if message.audio:
        file_id = message.audio.file_id
        storage.add_item(name, "audio", message.caption or "", file_id=file_id, caption=message.caption)
        await message.reply_text(f"Audio saved as '{name}'.")
        return

    if message.voice:
        file_id = message.voice.file_id
        storage.add_item(name, "voice", message.caption or "", file_id=file_id, caption=message.caption)
        await message.reply_text(f"Voice note saved as '{name}'.")
        return

    await message.reply_text("Unsupported message type.")


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("save", save_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("get", get_command))
    application.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO | filters.VIDEO | filters.DOCUMENT | filters.AUDIO | filters.VOICE,
            handle_message,
        )
    )

    try:
        application.run_polling(allowed_updates=["message"])
    except Conflict as exc:
        logging.error("Another bot instance is already running: %s", exc)
        raise


if __name__ == "__main__":
    main()
