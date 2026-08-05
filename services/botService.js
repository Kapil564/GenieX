export function getBotInfo() {
  return {
    name: "GenieX",
    description:
      "Automated bot that finds top AI news or matching GitHub commits and posts them to X.",
    version: "1.0.0",
  };
}

export function getHelpCommands() {
  return [
    { command: "/me", description: "Know about the bot" },
    { command: "/help", description: "See all available commands" },
    {
      command: "/setup",
      description: "Authorize GenieX to post to X (provide OAuth token)",
    },
    {
      command: "/rem",
      description: "Set a reminder for a later time",
      example: "/rem?time=2026-08-06T09:00",
    },
  ];
}

export function getTelegramCommands() {
  return getHelpCommands().map(({ command, description }) => ({
    command,
    description,
  }));
}

export function processCommand(command, time) {
  switch (command.toLowerCase()) {
    case "/me":
      return {
        command: "/me",
        response:
          "I am GenieX, an automated bot that finds AI news or relevant GitHub commits and posts them to X.",
      };

    case "/setup":
      // `time` parameter is reused here as an optional token in this demo
      if (!time) {
        return {
          command: "/setup",
          response:
            "To authorize GenieX, provide an OAuth token. For demo: GET /commands?cmd=/setup&token=YOUR_TOKEN (not secure).",
        };
      }

      return {
        command: "/setup",
        response:
          "Token received (demo). In production, GenieX would securely store and use the OAuth token to post on your behalf.",
      };

    case "/help":
      return {
        command: "/help",
        availableCommands: getHelpCommands(),
      };

    case "/rem":
      if (!time) {
        return {
          command: "/rem",
          error:
            "Missing time parameter. Add ?time=YYYY-MM-DDTHH:MM to set a reminder.",
        };
      }
      return {
        command: "/rem",
        response: `Reminder set for ${time}. I will remind you then.`,
      };

    default:
      return {
        command,
        error: "Unknown command. Use /help to see all available commands.",
      };
  }
}
