# 🚀 GitPushBot - Your GitHub Manager on Telegram

**GitPushBot** is a high-performance, open-source Telegram bot designed to bridge the gap between your local files and GitHub repositories. It allows developers to manage their code directly from the Telegram interface with ease and security.

---

## 🧐 What It Does
GitPushBot provides a seamless mobile-first experience for GitHub management. 
- **Pushes Files:** Send any document (code, images, text) to the bot, and it will instantly upload or update it in your repository.
- **Deletes Files:** Browse your repo and remove files you no longer need.
- **Navigates Directories:** Explore your repository structure through intuitive inline buttons.
- **Multi-Repo Support:** Switch between all your repositories in seconds.

## ⚙️ How It Works
1. **Authentication:** The bot uses your **GitHub Personal Access Token (PAT)**. This token is stored only within your Telegram session for maximum security.
2. **Session Logic:** It utilizes a `ConversationHandler` to guide you through selecting a repo and performing actions.
3. **API Integration:** Powered by `PyGithub`, it interacts with the GitHub REST API to perform file operations on the `main` branch.
4. **UI/UX:** Uses Telegram's HTML styling and inline keyboards for a modern, dashboard-like feel.

---

## 👨‍💻 Developed By
**GitPushBot** was created with ❤️ by **Ankur** ([@Ankurslys](https://t.me/Ankurslys)).

---

## 🚀 Setup & Installation

### For Normal Users
1. **Clone the Repo:**
   ```bash
   git clone https://github.com/ankurmoran96-openai/GitPushBot.git
   cd GitPushBot
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure:**
   Rename `config.py` and add your bot token, or use a `.env` file.
4. **Run:**
   ```bash
   python bot.py
   ```

## 📄 License
This project is licensed under the **MIT License**.
