import express from "express";
import dotenv from "dotenv";
import router from "./routes/index.js";
import errorHandler from "./middleware/errorHandler.js";
import { startTelegramBot } from "./services/telegrafBot.js";

const app = express();
dotenv.config();
const port = process.env.PORT ?? 3000;

app.use(express.json());
app.use("/", router);

app.use((req, res) => {
  res.status(404).json({ error: "Not found" });
});

app.use(errorHandler);

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  if (process.env.TELEGRAM_BOT_TOKEN) {
    startTelegramBot(process.env.TELEGRAM_BOT_TOKEN);
  }
});
