import express from "express";
import { registerTelegramCommands } from "../services/telegramService.js";

const router = express.Router();

router.get("/register", async (req, res) => {
  try {
    const result = await registerTelegramCommands(process.env.TELEGRAM_BOT_TOKEN);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
