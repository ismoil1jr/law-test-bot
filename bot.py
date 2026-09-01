import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler
from config import BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME, WEBAPP_URL
from database import SessionLocal, User, TestResult, Question
from datetime import datetime

logging.basicConfig(level=logging.INFO)

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

    # Profil rasmini olish
    photo_url = None
    try:
        photos = await update.effective_user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            file = await context.bot.get_file(file_id)
            photo_url = file.file_path
    except:
        pass

    # WebApp tugmasi (user_id va photo_url ni parametr sifatida yuboramiz)
    webapp_btn = InlineKeyboardButton(
        text="📝 Testni ochish",
        web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user_id}&photo={photo_url or ''}")
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
            if count <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❗️ Sonni to'g'ri kiriting (masalan: 5)")
            return

    db = SessionLocal()
    if target.isdigit():
        user = db.query(User).filter_by(user_id=int(target)).first()
    else:
        user = db.query(User).filter_by(username=target).first()

    if not user:
        await update.message.reply_text("❌ Bunday foydalanuvchi topilmadi!")
        db.close()
        return

    user.tests_remaining += count
    user.access_granted_at = datetime.now()
    db.commit()
    await update.message.reply_text(
        f"✅ @{user.username} ga {count} ta test huquqi berildi!\n"
        f"📊 Jami qolgan testlar: {user.tests_remaining}"
    )
    db.close()

# -------------------- ADMIN: SAVOL QO'SHISH --------------------
async def add_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return ConversationHandler.END

    await update.message.reply_text(
        "📝 **Yangi savol qo'shish**\n\n"
        "Savol matnini yozib yuboring. (Bekor qilish uchun /cancel)"
    )
    return ASK_TEXT

async def ask_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['text'] = update.message.text
    await update.message.reply_text("✏️ **Variant A** ni yozing:")
    return ASK_A

async def ask_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_a'] = update.message.text
    await update.message.reply_text("✏️ **Variant B** ni yozing:")
    return ASK_B

async def ask_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_b'] = update.message.text
    await update.message.reply_text("✏️ **Variant C** ni yozing:")
    return ASK_C

async def ask_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_c'] = update.message.text
    await update.message.reply_text("✏️ **Variant D** ni yozing:")
    return ASK_D

async def ask_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_d'] = update.message.text
    await update.message.reply_text("✅ **To'g'ri javob qaysi?** (A, B, C yoki D):")
    return ASK_CORRECT

async def ask_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    correct = update.message.text.upper()
    if correct not in ['A', 'B', 'C', 'D']:
        await update.message.reply_text("❌ Faqat A, B, C yoki D kiriting!")
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

    await update.message.reply_text(
        f"✅ **Savol qo'shildi!**\n\n"
        f"📝 {context.user_data['text']}\n"
        f"A) {context.user_data['option_a']}\n"
        f"B) {context.user_data['option_b']}\n"
        f"C) {context.user_data['option_c']}\n"
        f"D) {context.user_data['option_d']}\n"
        f"✅ To'g'ri: {correct}\n\n"
        f"Yana qo'shish uchun /add_question"
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    await update.message.reply_text("❌ Bekor qilindi.")
    context.user_data.clear()
    return ConversationHandler.END

# -------------------- ADMIN: SAVOLLAR RO'YXATI --------------------
async def list_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin emassiz!")
        return

    db = SessionLocal()
    questions = db.query(Question).all()
    db.close()

    if not questions:
        await update.message.reply_text("📚 Hozircha hech qanday savol yo'q.")
        return

    # Savollarni qisqa formatda chiqarish (har bir savol 1 qator)
    text = "📚 **Savollar ro'yxati:**\n\n"
    for idx, q in enumerate(questions, 1):
        text += f"`{idx}. {q.text[:30]}...` (ID: {q.id})\n"
        text += f"   A) {q.option_a[:15]} B) {q.option_b[:15]} C) {q.option_c[:15]} D) {q.option_d[:15]} → {q.correct_answer}\n\n"
        if len(text) > 3500:  # Telegram limiti 4096
            text += "\n... va boshqalar. /list_all bilan to'liq ko'ring."
            break

    await update.message.reply_text(text, parse_mode="Markdown")

# -------------------- ADMIN: SAVOLNI O'CHIRISH --------------------
async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin emassiz!")
        return

    args = context.args
    if not args:
        await update.message.reply_text("❗️ Ishlatish: /delete_question [ID]")
        return

    try:
        qid = int(args[0])
    except:
        await update.message.reply_text("❗️ ID son bo'lishi kerak!")
        return

    db = SessionLocal()
    q = db.query(Question).filter_by(id=qid).first()
    if not q:
        await update.message.reply_text("❌ Bunday ID li savol topilmadi!")
        db.close()
        return

    db.delete(q)
    db.commit()
    db.close()
    await update.message.reply_text(f"✅ {qid}-ID li savol o'chirildi!")

# -------------------- ADMIN: SAVOLNI YANGILASH --------------------
async def update_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin emassiz!")
        return

    args = context.args
    if len(args) < 6:
        await update.message.reply_text(
            "❗️ Ishlatish: /update_question [ID] [matn] [A] [B] [C] [D] [to'g'ri]\n"
            "Misol: /update_question 5 'Yangi savol?' 'Variant1' 'Variant2' 'Variant3' 'Variant4' A"
        )
        return

    try:
        qid = int(args[0])
        text = args[1]
        option_a = args[2]
        option_b = args[3]
        option_c = args[4]
        option_d = args[5]
        correct = args[6].upper()
        if correct not in ['A', 'B', 'C', 'D']:
            raise ValueError
    except:
        await update.message.reply_text("❗️ Ma'lumotlarni to'g'ri kiriting!")
        return

    db = SessionLocal()
    q = db.query(Question).filter_by(id=qid).first()
    if not q:
        await update.message.reply_text("❌ Bunday ID li savol topilmadi!")
        db.close()
        return

    q.text = text
    q.option_a = option_a
    q.option_b = option_b
    q.option_c = option_c
    q.option_d = option_d
    q.correct_answer = correct
    db.commit()
    db.close()

    await update.message.reply_text(f"✅ {qid}-ID li savol yangilandi!")

# -------------------- STATUS --------------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        await update.message.reply_text("❌ /start bosing")
        db.close()
        return
    await update.message.reply_text(
        f"📊 **Holatingiz:**\n"
        f"👤 ID: {user.user_id}\n"
        f"📝 Qolgan testlar: {user.tests_remaining}\n"
        f"📅 Oxirgi: {user.access_granted_at.strftime('%d.%m.%Y %H:%M') if user.access_granted_at else 'yoq'}"
    )
    db.close()

# -------------------- PLANS --------------------
async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📦 **Test paketlari:**\n\n"
        "🔹 5 ta test – 5 000 so'm\n"
        "🔹 10 ta test – 10 000 so'm\n"
        "🔹 15 ta test – 13 500 so'm\n\n"
        f"💳 Admin: @{ADMIN_USERNAME}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💬 Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

# -------------------- STATS --------------------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin emassiz!")
        return
    db = SessionLocal()
    total_users = db.query(User).count()
    total_results = db.query(TestResult).count()
    total_questions = db.query(Question).count()
    await update.message.reply_text(
        f"📊 **Statistika:**\n"
        f"👥 Foydalanuvchilar: {total_users}\n"
        f"📝 Natijalar: {total_results}\n"
        f"📚 Savollar: {total_questions}"
    )
    db.close()

# -------------------- ASOSIY --------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_question", add_question_start)],
        states={
            ASK_TEXT: [CommandHandler("cancel", cancel), CommandHandler("add_question", add_question_start)],
            ASK_A: [CommandHandler("cancel", cancel), CommandHandler("add_question", add_question_start)],
            ASK_B: [CommandHandler("cancel", cancel), CommandHandler("add_question", add_question_start)],
            ASK_C: [CommandHandler("cancel", cancel), CommandHandler("add_question", add_question_start)],
            ASK_D: [CommandHandler("cancel", cancel), CommandHandler("add_question", add_question_start)],
            ASK_CORRECT: [CommandHandler("cancel", cancel), CommandHandler("add_question", add_question_start)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(CommandHandler("list", list_questions))
    app.add_handler(CommandHandler("delete_question", delete_question))
    app.add_handler(CommandHandler("update_question", update_question))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()