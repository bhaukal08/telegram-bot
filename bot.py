import requests
from datetime import datetime, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# ===== CONFIG =====
NOTION_TOKEN = "ntn_Pw7690331805lj1NYpxeqefjjbLsFdAHGyWzZU8zrjxbep"
DATABASE_ID = "30002dd683dc80c8a20ad8124eee7195"
TELEGRAM_TOKEN = "8290096778:AAHyL54QzFqqZ07WbZLtek9oNW9MhZhLZaw"
CHAT_ID = "7027248897"

from datetime import datetime, timedelta


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

    today = datetime.now().date()
    today_tasks = []

    for page in data["results"]:
        props = page["properties"]

        # Task name
        title_list = props["Task"]["title"]
        if not title_list:
            continue
        task = title_list[0]["plain_text"]

        # Chapter
        chapter = props["Chapter"]["select"]["name"] if props["Chapter"]["select"] else "No Chapter"

        # Due date
        due = props["Due Date"]["date"]
        if not due:
            continue

        due_date = datetime.fromisoformat(due["start"].replace("Z", "+00:00")).date()

        # Filter: only today
        if due_date == today:
            today_tasks.append(f"• {chapter} - {task} - {due_date}")

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

# command handler
app.add_handler(CommandHandler("today", today))

# schedule job (9:00 AM daily)
app.job_queue.run_daily(send_daily, time(hour=9, minute=0))

print("🤖 Bot is running...")
app.run_polling()