import { getTelegramCommands } from "./botService.js";

export async function registerTelegramCommands(token) {
  if (!token) {
    throw new Error("Missing TELEGRAM_BOT_TOKEN");
  }

  const endpoint = `https://api.telegram.org/bot${token}/setMyCommands`;
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ commands: getTelegramCommands() }),
  });

  const result = await response.json();
  if (!result.ok) {
    throw new Error(
      result.description || "Telegram command registration failed",
    );
  }

  return result;
}
