# Discord Bot

A modular Discord bot with fun, moderation, utility, Islamic, and security features. Deployable on [Render](https://render.com/) with UptimeRobot health checks.

## Features
- Fun commands (AFK, polls, timers, invites, leaderboards, etc.)
- Moderation (purge, warn, mute, lock, etc.)
- Utility, Islamic, and security cogs
- Slash and classic command support
- Persistent settings with PostgreSQL
- Render/UptimeRobot-ready health check

## Setup
1. **Clone the repo:**
   ```sh
   git clone soon
   cd YOUR-REPO
   ```
2. **Install dependencies:**
   ```sh
   pip install -r BOTHOST/render/uptimerobot/requirements.txt
   ```
3. **Set environment variables:**
   - `DISCORD_TOKEN`: Your Discord bot token
   - (Optional) Database connection variables if using PostgreSQL

## Local Run
```sh
python bot.py
```

## Deploy on Render
1. Push your code to GitHub.
2. Create a new **Web Service** on Render.
3. Set the start command to:
   ```sh
   python BOTHOST/render/uptimerobot/server.py
   ```
4. Add the environment variable `DISCORD_TOKEN` with your bot token.
5. (Optional) Add your database environment variables.
6. UptimeRobot can ping your Render URL (e.g., `https://your-app.onrender.com/`).

## Health Check
The bot exposes a `/` endpoint for UptimeRobot/Render health checks.

---

**Made with ❤️ by gh_sman** 