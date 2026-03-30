# GitHub Manager Bot Configuration (Open-Source Template)
# Rename this to config.py and fill in the values.

import os
from dotenv import load_dotenv

load_dotenv()

# Your Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
