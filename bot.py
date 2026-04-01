import requests
import os
from datetime import datetime, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== CONFIG FROM ENV =====
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# 📊 FUNCTION: GET TODAY TASKS
# =========================
def get_today_tasks():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers)
    data = response.json()

    today_tasks = []

    # ✅ define once (outside loop)
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")

    for page in data["results"]:
        props = page["properties"]

        title_list = props["Task"]["title"]
        if not title_list:
            continue
        task = title_list[0]["plain_text"]

        chapter = props["Chapter"]["select"]["name"] if props["Chapter"]["select"] else "No Chapter"

        due = props["Due Date"]["date"]
        if not due:
            continue

        raw_date = due["start"]
        due_date = raw_date[:10]

        if due_date == today_str:
            today_tasks.append(f"• {chapter} - {task} - {due_date}")

    # =========================
    # 📝 FORMAT MESSAGE
    # =========================
    message = "📚 *Today's To Do*\n\n"

    if today_tasks:
        message += "\n".join(today_tasks)
    else:
        message += "No tasks for today 😄"

    return message
# =========================
# 🤖 COMMAND: /today
# =========================
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = get_today_tasks()
    await update.message.reply_text(message, parse_mode="Markdown")

# =========================
# ⏰ AUTO SEND DAILY
# =========================
async def send_daily(context: ContextTypes.DEFAULT_TYPE):
    message = get_today_tasks()
    await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# =========================
# 🚀 START BOT
# =========================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("today", today))

app.job_queue.run_daily(send_daily, time(hour=9, minute=0))

print("🤖 Bot is running...")
app.run_polling()