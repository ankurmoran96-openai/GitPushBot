# 🚀 GitPushBot - GitHub File Manager

GitPushBot is a powerful Telegram bot that allows you to manage your GitHub repositories directly from Telegram. You can upload (push) files, delete files, and navigate through your repository structure with ease.

## ✨ Features

- **Direct Upload:** Send any file to the bot, and it will push it to your selected GitHub repository.
- **File Management:** List and delete files in your repositories.
- **Directory Navigation:** Browse through folders in your repositories.
- **Secure:** Uses GitHub Personal Access Tokens (PAT) which are only stored in your session.
- **Open Source:** Easy to deploy and customize.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- A GitHub Personal Access Token (PAT) with `repo` permissions.

### 2. Installation
```bash
git clone https://github.com/ankurmoran96-openai/GitPushBot.git
cd GitPushBot
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory and add your Telegram Bot Token:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot
```bash
python bot.py
```

## 🛠 Tech Stack
- **[python-telegram-bot](https://python-telegram-bot.org/)**: Telegram API wrapper.
- **[PyGithub](https://github.com/PyGithub/PyGithub)**: GitHub API library.
- **[python-dotenv](https://github.com/theskumar/python-dotenv)**: Environment variable management.

## 👨‍💻 Developer
Created with ❤️ by [Ankur](https://t.me/Ankurslys).

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
