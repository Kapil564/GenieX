import express from "express";
import { getBotInfo } from "../services/botService.js";

const router = express.Router();

router.get("/", (req, res) => {
  res.json(getBotInfo());
});

export default router;
