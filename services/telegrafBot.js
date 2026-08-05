import { Telegraf } from "telegraf";
import { processCommand, getHelpCommands } from "./botService.js";

let botInstance = null;

export function startTelegramBot(token) {
  if (!token) return null;
  try {
    const bot = new Telegraf(token);

    bot.start((ctx) =>
      ctx.reply("Hello from GenieX! Use /help to see commands."),
    );

    bot.command("me", (ctx) => {
      const res = processCommand("/me");
      ctx.reply(res.response);
    });

    bot.command("help", (ctx) => {
      const res = processCommand("/help");
      const lines = res.availableCommands
        .map((c) => `${c.command} — ${c.description}`)
        .join("\n");
      ctx.reply(lines);
    });

    bot.command("rem", (ctx) => {
      const text = ctx.message.text || "";
      const arg = text.split(" ").slice(1).join(" ");
      const res = processCommand("/rem", arg || undefined);
      if (res.error) ctx.reply(res.error);
      else ctx.reply(res.response);
    });

    bot.command("setup", (ctx) => {
      const text = ctx.message.text || "";
      const tokenArg = text.split(" ").slice(1).join(" ");
      if (!tokenArg) {
        ctx.reply(
          "To authorize GenieX, reply with: /setup <YOUR_X_OAUTH_TOKEN> (demo).",
        );
        return;
      }

      // Demo behavior: do not store tokens in this sample code.
      ctx.reply(
        "Token received (demo). In production, GenieX would securely store and use the OAuth token to post on your behalf.",
      );
    });

    bot.launch();
    botInstance = bot;
    console.log("GenieX Telegram bot started (polling).");
    return bot;
  } catch (err) {
    console.error("Failed to start Telegraf bot:", err.message || err);
    return null;
  }
}

export function stopTelegramBot() {
  if (botInstance) {
    botInstance.stop();
    botInstance = null;
  }
}
