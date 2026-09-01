import logging
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

ADMIN_IDS = [int(i.strip()) for i in os.environ.get('ADMIN_ID', '5690099705,6106446622').split(',') if i.strip()]
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', "erkinvv17")
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

# -------------------- HOLATLAR --------------------
# Savol qo'shish holatlari
ASK_TEXT, ASK_A, ASK_B, ASK_C, ASK_D, ASK_CORRECT = range(6)
# Savol tahrirlash holatlari
EDIT_TEXT, EDIT_A, EDIT_B, EDIT_C, EDIT_D, EDIT_CORRECT = range(6, 12)

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
    if update.effective_user.id not in ADMIN_IDS:
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

# -------------------- ADMIN: SAVOLLAR RO'YXATI --------------------
async def list_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Faqat admin!")
        return

    db = SessionLocal()
    questions = db.query(Question).all()
    db.close()

    if not questions:
        await update.message.reply_text("📭 Bazada hech qanday savol topilmadi.")
        return

    msg = "📋 Baza savollari ro'yxati:\n\n"
    for q in questions[:20]:
        msg += f"🆔 {q.id}: {q.text[:40]}... (To'g'ri: {q.correct_answer})\n"

    msg += f"\n📊 Jami savollar: {len(questions)} ta"
    msg += "\n✏️ Tahrirlash: /update_question ID"
    msg += "\n🗑 O'chirish: /delete_question ID"

    await update.message.reply_text(msg)
# -------------------- ADMIN: SAVOLNI O'CHIRISH --------------------
async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Faqat admin!")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗️ Ishlatish: `/delete_question ID` (masalan: `/delete_question 1`)", parse_mode="Markdown")
        return

    q_id = int(context.args[0])
    db = SessionLocal()
    q = db.query(Question).filter_by(id=q_id).first()

    if not q:
        await update.message.reply_text("❌ Bunday ID ga ega savol topilmadi.")
        db.close()
        return

    db.delete(q)
    db.commit()
    db.close()
    await update.message.reply_text(f"✅ ID #{q_id} bo'lgan savol o'chirildi!")

# -------------------- ADMIN: SAVOL QO'SHISH --------------------
async def add_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
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

# -------------------- ADMIN: SAVOLNI TAHRIRLASH --------------------
async def update_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Faqat admin!")
        return ConversationHandler.END

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗️ Ishlatish: `/update_question ID` (masalan: `/update_question 1`)", parse_mode="Markdown")
        return ConversationHandler.END

    q_id = int(context.args[0])
    db = SessionLocal()
    q = db.query(Question).filter_by(id=q_id).first()
    db.close()

    if not q:
        await update.message.reply_text("❌ Bunday ID ga ega savol topilmadi.")
        return ConversationHandler.END

    context.user_data['edit_id'] = q_id
    await update.message.reply_text(f"✏️ ID #{q_id} uchun yangi savol matnini kiriting:")
    return EDIT_TEXT

async def edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_text'] = update.message.text
    await update.message.reply_text("✏️ Yangi Variant A:")
    return EDIT_A

async def edit_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_a'] = update.message.text
    await update.message.reply_text("✏️ Yangi Variant B:")
    return EDIT_B

async def edit_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_b'] = update.message.text
    await update.message.reply_text("✏️ Yangi Variant C:")
    return EDIT_C

async def edit_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_c'] = update.message.text
    await update.message.reply_text("✏️ Yangi Variant D:")
    return EDIT_D

async def edit_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_d'] = update.message.text
    await update.message.reply_text("✅ Yangi to'g'ri javob (A/B/C/D):")
    return EDIT_CORRECT

async def edit_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    correct = update.message.text.upper()
    if correct not in ['A','B','C','D']:
        await update.message.reply_text("❌ Faqat A, B, C yoki D")
        return EDIT_CORRECT

    q_id = context.user_data['edit_id']
    db = SessionLocal()
    q = db.query(Question).filter_by(id=q_id).first()

    if q:
        q.text = context.user_data['edit_text']
        q.option_a = context.user_data['edit_a']
        q.option_b = context.user_data['edit_b']
        q.option_c = context.user_data['edit_c']
        q.option_d = context.user_data['edit_d']
        q.correct_answer = correct
        db.commit()
        await update.message.reply_text(f"✅ ID #{q_id} savoli muvaffaqiyatli yangilandi!")
    else:
        await update.message.reply_text("❌ Xatolik yuz berdi.")

    db.close()
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
        [InlineKeyboardButton("💬 Admin", url=f"https://t.me/{ADMIN_USERNAME.split(',')[0]}")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)

# -------------------- ASOSIY FUNKSIYA --------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add_question", add_question_start)],
        states={
            ASK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_text)],
            ASK_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_a)],
            ASK_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_b)],
            ASK_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_c)],
            ASK_D: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_d)],
            ASK_CORRECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_correct)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    update_conv = ConversationHandler(
        entry_points=[CommandHandler("update_question", update_question_start)],
        states={
            EDIT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_text)],
            EDIT_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_a)],
            EDIT_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_b)],
            EDIT_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_c)],
            EDIT_D: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_d)],
            EDIT_CORRECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_correct)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CommandHandler("list", list_questions))
    app.add_handler(CommandHandler("delete_question", delete_question))
    app.add_handler(add_conv)
    app.add_handler(update_conv)

    app.run_polling()

if __name__ == "__main__":
    main()