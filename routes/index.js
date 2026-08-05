import express from "express";
import aboutRouter from "./about.js";
import commandsRouter from "./commands.js";
import telegramRouter from "./telegram.js";

const router = express.Router();

router.use("/about", aboutRouter);
router.use("/commands", commandsRouter);
router.use("/telegram", telegramRouter);

export default router;
