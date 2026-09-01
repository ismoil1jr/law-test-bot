import logging
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from database import SessionLocal, User, TestResult, Question
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# -------------------- ENVIRONMENT VARIABLES --------------------
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is not set!")

ADMIN_ID = int(os.environ.get('ADMIN_ID', 5690099705))
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', "erkinvv17")
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

# -------------------- HOLATLAR --------------------
ASK_TEXT, ASK_A, ASK_B, ASK_C, ASK_D, ASK_CORRECT = range(6)

# -------------------- START --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id, username=username, full_name=full_name)
        db.add(user)
        db.commit()

    webapp_btn = InlineKeyboardButton(
        text="📝 Testni ochish",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    keyboard = InlineKeyboardMarkup([[webapp_btn]])
    await update.message.reply_text(
        f"Assalomu alaykum, {full_name}!\n"
        f"⚖️ Huquqiy test botiga xush kelibsiz.\n\n"
        f"📊 Qolgan testlar: {user.tests_remaining}\n\n"
        f"⬇️ Testni boshlash uchun tugmani bosing.",
        reply_markup=keyboard
    )
    db.close()

# -------------------- ADMIN: GRANT --------------------
async def grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗️ Ishlatish: /grant @username [son]")
        return
    target = args[0].replace("@", "")
    count = 1
    if len(args) >= 2:
        try:
            count = int(args[1])
        except:
            await update.message.reply_text("❗️ Sonni to'g'ri kiriting")
            return
    db = SessionLocal()
    if target.isdigit():
        user = db.query(User).filter_by(user_id=int(target)).first()
    else:
        user = db.query(User).filter_by(username=target).first()
    if not user:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi")
        db.close()
        return
    user.tests_remaining += count
    user.access_granted_at = datetime.now()
    db.commit()
    await update.message.reply_text(f"✅ @{user.username} ga {count} ta test berildi! (Jami: {user.tests_remaining})")
    db.close()

# -------------------- ADMIN: SAVOL QO'SHISH --------------------
async def add_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Faqat admin!")
        return ConversationHandler.END
    await update.message.reply_text("📝 Savol matnini yozing:")
    return ASK_TEXT

async def ask_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['text'] = update.message.text
    await update.message.reply_text("✏️ Variant A:")
    return ASK_A

async def ask_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_a'] = update.message.text
    await update.message.reply_text("✏️ Variant B:")
    return ASK_B

async def ask_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_b'] = update.message.text
    await update.message.reply_text("✏️ Variant C:")
    return ASK_C

async def ask_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_c'] = update.message.text
    await update.message.reply_text("✏️ Variant D:")
    return ASK_D

async def ask_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_d'] = update.message.text
    await update.message.reply_text("✅ To'g'ri javob (A/B/C/D):")
    return ASK_CORRECT

async def ask_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    correct = update.message.text.upper()
    if correct not in ['A','B','C','D']:
        await update.message.reply_text("❌ Faqat A, B, C yoki D")
        return ASK_CORRECT
    db = SessionLocal()
    q = Question(
        text=context.user_data['text'],
        option_a=context.user_data['option_a'],
        option_b=context.user_data['option_b'],
        option_c=context.user_data['option_c'],
        option_d=context.user_data['option_d'],
        correct_answer=correct
    )
    db.add(q)
    db.commit()
    db.close()
    await update.message.reply_text("✅ Savol qo'shildi!")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi")
    context.user_data.clear()
    return ConversationHandler.END

# -------------------- STATUS --------------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.message.reply_text("❌ /start bosing")
        db.close()
        return
    await update.message.reply_text(f"📊 Qolgan testlar: {user.tests_remaining}")
    db.close()

# -------------------- PLANS --------------------
async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📦 Paketlar:\n5 ta – 5000 so'm\n10 ta – 10000 so'm\n15 ta – 13500 so'm"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)

# -------------------- ASOSIY FUNKSIYA (ASINXRON!) --------------------
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("add_question", add_question_start)],
        states={
            ASK_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_text),
                CommandHandler("cancel", cancel)
            ],
            ASK_A: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_a),
                CommandHandler("cancel", cancel)
            ],
            ASK_B: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_b),
                CommandHandler("cancel", cancel)
            ],
            ASK_C: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_c),
                CommandHandler("cancel", cancel)
            ],
            ASK_D: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_d),
                CommandHandler("cancel", cancel)
            ],
            ASK_CORRECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_correct),
                CommandHandler("cancel", cancel)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(conv)
    await app.run_polling()

# -------------------- ISHGA TUSHIRISH --------------------
if __name__ == "__main__":
    asyncio.run(main())