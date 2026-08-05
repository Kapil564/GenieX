export function getBotInfo() {
  return {
    name: "Telegram Bot",
    description: "Demo API for GitHub Actions CI/CD learning",
    version: "1.0.0",
  };
}

export function getHelpCommands() {
  return [
    { command: "/me", description: "Know about the bot" },
    { command: "/help", description: "See all available commands" },
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
          "I am Telegram Bot, a demo API built to learn GitHub Actions CI/CD.",
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
