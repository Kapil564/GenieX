# Telegram Bot CI/CD Demo

A lightweight Express API designed as a learning project for GitHub Actions CI/CD.

This repository includes:

- A simple Node.js/Express HTTP API
- A service layer for bot-related logic
- Automated tests using Node's built-in test runner
- A GitHub Actions workflow that installs dependencies and runs tests on push and pull requests

## Commands

- `npm install`
- `npm start`
- `npm run dev`
- `npm test`

## API

- `GET /about` — project metadata
- `GET /commands?cmd=/help` — bot commands and usage
- `GET /telegram/register` — register bot commands with Telegram using `TELEGRAM_BOT_TOKEN`

## Learning goals

- Practice GitHub Actions workflow configuration
- Validate Node.js app behavior with automated tests
- Learn basic repo structure for CI/CD-ready apps
