# GitPushBot Configuration Template
# For normal users: Fill in your TELEGRAM_BOT_TOKEN here.
# For advanced users: Use a .env file.

import os
from dotenv import load_dotenv

load_dotenv()

# Replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
