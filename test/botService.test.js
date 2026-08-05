import assert from "assert";
import {
  getBotInfo,
  getHelpCommands,
  processCommand,
} from "../services/botService.js";

const botInfo = getBotInfo();
assert.strictEqual(botInfo.name, "Telegram Bot", "Bot name should match");
assert.ok(
  botInfo.description.includes("CI/CD"),
  "Description should mention CI/CD",
);

const help = getHelpCommands();
assert.strictEqual(help.length, 3, "Help should include three commands");
assert.strictEqual(help[0].command, "/me");
assert.strictEqual(help[1].command, "/help");
assert.strictEqual(help[2].command, "/rem");

const meResponse = processCommand("/me");
assert.strictEqual(meResponse.command, "/me");
assert.ok(meResponse.response.includes("Telegram Bot"));

const helpResponse = processCommand("/help");
assert.strictEqual(helpResponse.command, "/help");
assert.strictEqual(helpResponse.availableCommands.length, 3);

const remResponse = processCommand("/rem", "2026-08-06T09:00");
assert.strictEqual(remResponse.command, "/rem");
assert.ok(remResponse.response.includes("Reminder set for 2026-08-06T09:00"));

const remError = processCommand("/rem");
assert.strictEqual(remError.command, "/rem");
assert.ok(remError.error.includes("Missing time parameter"));

const unknown = processCommand("/unknown");
assert.strictEqual(unknown.error, "Unknown command. Use /help to see all available commands.");
