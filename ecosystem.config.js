module.exports = {
  apps: [{
    name: "bot",
    script: "bot.py",
    cwd: "/root/hosting_bot/tg_bot_zep",
    interpreter: "/root/hosting_bot/tg_bot_zep/.venv/bin/python",
    autorestart: true,
    restart_delay: 5000
  }]
}
