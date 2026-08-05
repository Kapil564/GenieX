import express from "express";
import { getBotInfo, getHelpCommands, processCommand } from "../services/botService.js";

const router = express.Router();

router.get("/", (req, res) => {
  const command = String(req.query.cmd || req.query.command || "").trim();
  const time = req.query.time ? String(req.query.time).trim() : undefined;

  if (!command) {
    return res.status(400).json({
      error: "Command is required. Use ?cmd=/me, ?cmd=/help, or ?cmd=/rem",
    });
  }

  const result = processCommand(command, time);
  return res.json(result);
});

export default router;
