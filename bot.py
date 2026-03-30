import os
import logging
from github import Github
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for ConversationHandler
SETTING_TOKEN, SELECTING_REPO, SELECTING_ACTION, LISTING_CONTENTS = range(4)

# UI Constant
BANNER = "<b>🚀 GitPushBot | GitHub Manager</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"

def get_github_client(context: ContextTypes.DEFAULT_TYPE):
    """Get GitHub client for the current user."""
    token = context.user_data.get('github_token')
    if not token:
        return None
    return Github(token)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the bot and check for GitHub token."""
    user = update.effective_user
    if 'github_token' not in context.user_data:
        welcome_text = (
            f"{BANNER}"
            f"Hello, <b>{user.first_name}</b>! 👋\n\n"
            "To manage your repositories, please provide your <b>GitHub Personal Access Token (PAT)</b>.\n\n"
            "🔑 <i>How to get one: Settings > Developer Settings > Personal Access Tokens > Tokens (classic).</i>\n\n"
            "🛡 <b>Security:</b> Ensure you grant <code>repo</code> permissions."
        )
        await update.message.reply_html(welcome_text)
        return SETTING_TOKEN
    
    return await list_repos(update, context)

async def receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate and store the user's GitHub token."""
    token = update.message.text.strip()
    
    try:
        g = Github(token)
        user = g.get_user()
        username = user.login
        
        context.user_data['github_token'] = token
        context.user_data['github_username'] = username
        
        await update.message.reply_html(f"✅ <b>Token Verified!</b>\nWelcome, <code>{username}</code>. Fetching your repositories...")
        return await list_repos(update, context)
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        await update.message.reply_html("❌ <b>Invalid Token</b> or connection error.\nPlease send a valid GitHub PAT.")
        return SETTING_TOKEN

async def list_repos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """List repositories for the user."""
    g = get_github_client(context)
    if not g:
        await update.effective_message.reply_html("⚠️ <b>Session Expired.</b> Please use /start.")
        return ConversationHandler.END

    loading_msg = await update.effective_message.reply_html("🔄 <b>Fetching repositories...</b>")
    
    try:
        user_gh = g.get_user()
        repos = user_gh.get_repos()
        
        keyboard = []
        for repo in repos:
            keyboard.append([InlineKeyboardButton(f"📁 {repo.name}", callback_data=f"repo:{repo.name}")])
        
        if not keyboard:
            await loading_msg.edit_text("❌ No repositories found.")
            return ConversationHandler.END

        reply_markup = InlineKeyboardMarkup(keyboard)
        await loading_msg.edit_text(f"{BANNER}<b>Select a Repository:</b>", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return SELECTING_REPO
    except Exception as e:
        logger.error(f"Error fetching repos: {e}")
        await loading_msg.edit_text("❌ Failed to fetch repositories. Use /logout and try again.")
        return ConversationHandler.END

async def repo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    repo_name = query.data.split(":")[1]
    context.user_data['repo_name'] = repo_name
    context.user_data['current_path'] = ""
    
    keyboard = [
        [InlineKeyboardButton("📤 Initiate (Upload File)", callback_data="initiate")],
        [InlineKeyboardButton("🗑 Delete File", callback_data="list_contents")],
        [InlineKeyboardButton("🔙 Back to Repos", callback_data="back_to_repos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"{BANNER}"
        f"📍 <b>Repo:</b> <code>{repo_name}</code>\n\n"
        "What would you like to do?", 
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return SELECTING_ACTION

async def list_contents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    repo_name = context.user_data['repo_name']
    path = context.user_data.get('current_path', "")
    g = get_github_client(context)
    repo = g.get_user().get_repo(repo_name)
    
    try:
        contents = repo.get_contents(path)
        keyboard = []
        
        if path:
            parent_path = "/".join(path.split("/")[:-1])
            keyboard.append([InlineKeyboardButton("📁 .. (Parent)", callback_data=f"cd:{parent_path}")])

        for content in contents:
            if content.type == "dir":
                keyboard.append([InlineKeyboardButton(f"📁 {content.path}", callback_data=f"cd:{content.path}")])
            else:
                keyboard.append([InlineKeyboardButton(f"📄 {content.path}", callback_data=f"delete:{content.path}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        display_path = path if path else "Root"
        await query.edit_message_text(
            f"{BANNER}"
            f"📂 <b>Path:</b> <code>{repo_name}/{display_path}</code>\n\n"
            "<i>Select a file to DELETE or folder to navigate.</i>", 
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return LISTING_CONTENTS
    except Exception as e:
        logger.error(f"Error listing contents: {e}")
        await query.edit_message_text(f"❌ Error listing contents: {e}")
        return SELECTING_ACTION

async def handle_cd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    path = query.data.split(":")[1]
    context.user_data['current_path'] = path
    return await list_contents(update, context)

async def delete_file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    file_path = query.data.split(":")[1]
    repo_name = context.user_data['repo_name']
    g = get_github_client(context)
    repo = g.get_user().get_repo(repo_name)
    
    try:
        contents = repo.get_contents(file_path)
        repo.delete_file(contents.path, f"Deleted {file_path} via Bot", contents.sha, branch="main")
        await query.edit_message_text(f"✅ <b>Successfully Deleted:</b>\n<code>{file_path}</code>")
        return await show_action_menu(update, context)
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        await query.edit_message_text(f"❌ <b>Deletion Failed:</b>\n{e}")
        return SELECTING_ACTION

async def initiate_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"{BANNER}"
        "📤 <b>Send the file</b> you want to upload to the <code>main</code> branch.",
        parse_mode=ParseMode.HTML
    )
    return SELECTING_ACTION

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    repo_name = context.user_data.get('repo_name')
    if not repo_name:
        await update.message.reply_html("⚠️ <b>Select a repository first!</b>")
        return ConversationHandler.END
        
    document = update.message.document
    file_name = document.file_name
    
    status_msg = await update.message.reply_html(f"🔄 <b>Uploading</b> <code>{file_name}</code>...")
    
    try:
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()
        
        g = get_github_client(context)
        repo = g.get_user().get_repo(repo_name)
        
        try:
            contents = repo.get_contents(file_name, ref="main")
            repo.update_file(contents.path, f"Update {file_name} via Bot", bytes(file_bytes), contents.sha, branch="main")
            await status_msg.edit_text(f"✅ <b>Updated:</b> <code>{file_name}</code>", parse_mode=ParseMode.HTML)
        except:
            repo.create_file(file_name, f"Upload {file_name} via Bot", bytes(file_bytes), branch="main")
            await status_msg.edit_text(f"✅ <b>Uploaded:</b> <code>{file_name}</code>", parse_mode=ParseMode.HTML)
            
        return await show_action_menu_message(update, context)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        await update.message.reply_html(f"❌ <b>Upload Failed:</b>\n{e}")
        return SELECTING_ACTION

async def show_action_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    repo_name = context.user_data['repo_name']
    keyboard = [
        [InlineKeyboardButton("📤 Initiate (Upload File)", callback_data="initiate")],
        [InlineKeyboardButton("🗑 Delete File", callback_data="list_contents")],
        [InlineKeyboardButton("🔙 Back to Repos", callback_data="back_to_repos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_text = f"{BANNER}📍 <b>Repo:</b> <code>{repo_name}</code>\nWhat's next?"
    if update.callback_query:
        await update.callback_query.message.reply_html(msg_text, reply_markup=reply_markup)
    else:
        await update.message.reply_html(msg_text, reply_markup=reply_markup)
    return SELECTING_ACTION

async def show_action_menu_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await show_action_menu(update, context)

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    return await show_action_menu(update, context)

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_html("👋 <b>Logged Out.</b> Your session has been cleared.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_html("❌ <b>Operation Cancelled.</b>")
    return ConversationHandler.END

async def set_token_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_html("🔑 <b>Please send your NEW GitHub PAT:</b>")
    return SETTING_TOKEN

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html("🏓 <b>Pong!</b> Bot is active.")

def main():
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("ping", ping))
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("set_token", set_token_command)
        ],
        states={
            SETTING_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_token)],
            SELECTING_REPO: [CallbackQueryHandler(repo_choice, pattern="^repo:")],
            SELECTING_ACTION: [
                CallbackQueryHandler(initiate_prompt, pattern="^initiate$"),
                CallbackQueryHandler(list_contents, pattern="^list_contents$"),
                CallbackQueryHandler(list_repos, pattern="^back_to_repos$"),
                MessageHandler(filters.Document.ALL, handle_document),
            ],
            LISTING_CONTENTS: [
                CallbackQueryHandler(handle_cd, pattern="^cd:"),
                CallbackQueryHandler(delete_file_callback, pattern="^delete:"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("logout", logout), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("logout", logout))
    application.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, handle_document))

    logger.info("Bot started...")
    application.run_polling()

if __name__ == "__main__":
    main()
