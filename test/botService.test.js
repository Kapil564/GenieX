import assert from "assert";
import {
  getBotInfo,
  getHelpCommands,
  processCommand,
} from "../services/botService.js";

const botInfo = getBotInfo();
assert.strictEqual(botInfo.name, "GenieX", "Bot name should match");
assert.ok(
  botInfo.description.includes("AI news") || botInfo.description.includes("X"),
  "Description should mention AI news or X",
);

const help = getHelpCommands();
assert.strictEqual(help.length, 4, "Help should include four commands");
assert.strictEqual(help[0].command, "/me");
assert.strictEqual(help[1].command, "/help");
assert.strictEqual(help[2].command, "/rem");
assert.strictEqual(help[3].command, "/setup");

const meResponse = processCommand("/me");
assert.strictEqual(meResponse.command, "/me");
assert.ok(meResponse.response.includes("GenieX"));

const setupPrompt = processCommand("/setup");
assert.strictEqual(setupPrompt.command, "/setup");
assert.ok(setupPrompt.response.includes("provide an OAuth token"));

const setupWithToken = processCommand("/setup", "demo-token-123");
assert.strictEqual(setupWithToken.command, "/setup");
assert.ok(setupWithToken.response.includes("Token received"));

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
assert.strictEqual(
  unknown.error,
  "Unknown command. Use /help to see all available commands.",
);
