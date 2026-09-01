import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from database import SessionLocal, User, TestResult, Question
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# -------------------- KONFIGURATSIYA --------------------
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN o'rnatilmagan!")

ADMIN_IDS = [int(i.strip()) for i in os.environ.get('ADMIN_ID', '5690099705,6106446622').split(',') if i.strip()]
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', "erkinvv17")
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

# -------------------- HOLATLAR --------------------
ASK_TEXT, ASK_A, ASK_B, ASK_C, ASK_D, ASK_CORRECT = range(6)
EDIT_TEXT, EDIT_A, EDIT_B, EDIT_C, EDIT_D, EDIT_CORRECT = range(6, 12)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

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
    else:
        # Username va ism o'zgargan bo'lsa yangilaymiz
        user.username = username
        user.full_name = full_name
    db.commit()

    buttons = [[InlineKeyboardButton("📝 Testni ochish", web_app=WebAppInfo(url=WEBAPP_URL))]]
    
    if is_admin(user_id):
        buttons.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        f"Assalomu alaykum, {full_name}!\n"
        f"⚖️ Huquqiy test botiga xush kelibsiz.\n\n"
        f"📊 Qolgan testlar: {user.tests_remaining}\n\n"
        f"⬇️ Testni boshlash uchun tugmani bosing.",
        reply_markup=keyboard
    )
    db.close()

# -------------------- ADMIN PANEL MENUSI --------------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    if not is_admin(user_id):
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Savol qo'shish", callback_data="btn_add_q")],
        [InlineKeyboardButton("📋 Savollar ro'yxati", callback_data="btn_list_q")],
        [InlineKeyboardButton("📊 Baza statistikasi", callback_data="btn_stats_q")],
        [InlineKeyboardButton("🎁 Test berish qo'llanmasi", callback_data="btn_grant_info")]
    ])

    text = "🛠 **Admin Boshqaruv Paneli**\n\nKerakli bo'limni tanlang:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

# -------------------- CALLBACK QUERY HANDLER --------------------
async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if not is_admin(user_id):
        return

    if data == "admin_panel":
        await admin_panel(update, context)

    elif data == "btn_list_q":
        await list_questions_callback(query)

    elif data == "btn_stats_q":
        db = SessionLocal()
        q_count = db.query(Question).count()
        u_count = db.query(User).count()
        r_count = db.query(TestResult).count()
        db.close()
        
        msg = f"📊 **Statistika:**\n\n👥 Foydalanuvchilar: {u_count} ta\n❓ Savollar: {q_count} ta\n📝 Yechilgan testlar: {r_count} ta"
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]])
        await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")

    elif data == "btn_grant_info":
        msg = "🎁 **Foydalanuvchiga test berish:**\n\nBuyruq shakli:\n`/grant @username 5`\nyoki ID orqali:\n`/grant 12345678 5`"
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]])
        await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")

    elif data.startswith("del_q_"):
        q_id = int(data.split("_")[2])
        db = SessionLocal()
        q = db.query(Question).filter_by(id=q_id).first()
        if q:
            db.delete(q)
            db.commit()
            await query.message.edit_text(f"✅ ID #{q_id} savoli o'chirildi!")
        else:
            await query.message.edit_text("❌ Savol topilmadi.")
        db.close()

# -------------------- SAVOLLAR RO'YXATI (BUTTONS) --------------------
async def list_questions_callback(query):
    db = SessionLocal()
    questions = db.query(Question).order_by(Question.id.desc()).limit(15).all()
    db.close()

    if not questions:
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]])
        await query.message.edit_text("📭 Bazada hech qanday savol topilmadi.", reply_markup=back_btn)
        return

    msg = "📋 **So'nggi savollar ro'yxati:**\n\n"
    buttons = []
    for q in questions:
        msg += f"🆔 **{q.id}**: {q.text[:35]}... (To'g'ri: {q.correct_answer})\n"
        buttons.append([
            InlineKeyboardButton(f"✏️ #{q.id} Tahrirlash", callback_data=f"edit_info_{q.id}"),
            InlineKeyboardButton(f"🗑 #{q.id} O'chirish", callback_data=f"del_q_{q.id}")
        ])

    buttons.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")])
    await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

# -------------------- SAVOL QO'SHISH (CONVERSATION) --------------------
async def add_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        message_func = query.message.reply_text
    else:
        user_id = update.effective_user.id
        message_func = update.message.reply_text

    if not is_admin(user_id):
        return ConversationHandler.END

    await message_func("📝 **Yangi savol matnini yozing:**", parse_mode="Markdown")
    return ASK_TEXT

async def ask_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['text'] = update.message.text
    await update.message.reply_text("✏️ **Variant A:**", parse_mode="Markdown")
    return ASK_A

async def ask_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_a'] = update.message.text
    await update.message.reply_text("✏️ **Variant B:**", parse_mode="Markdown")
    return ASK_B

async def ask_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_b'] = update.message.text
    await update.message.reply_text("✏️ **Variant C:**", parse_mode="Markdown")
    return ASK_C

async def ask_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_c'] = update.message.text
    await update.message.reply_text("✏️ **Variant D:**", parse_mode="Markdown")
    return ASK_D

async def ask_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['option_d'] = update.message.text
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("A", callback_data="ans_A"), InlineKeyboardButton("B", callback_data="ans_B")],
        [InlineKeyboardButton("C", callback_data="ans_C"), InlineKeyboardButton("D", callback_data="ans_D")]
    ])
    await update.message.reply_text("✅ **To'g'ri variantni tanlang:**", reply_markup=keyboard, parse_mode="Markdown")
    return ASK_CORRECT

async def ask_correct_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    correct = query.data.replace("ans_", "")

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

    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")]])
    await query.message.edit_text(f"✅ Savol muvaffaqiyatli qo'shildi! (To'g'ri javob: {correct})", reply_markup=back_btn)
    context.user_data.clear()
    return ConversationHandler.END

# -------------------- TAHRIRLASH QO'LLANMA --------------------
async def edit_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    q_id = query.data.split("_")[2]
    await query.message.reply_text(f"✏️ Tahrirlash uchun `/update_question {q_id}` buyrug'ini yuboring.", parse_mode="Markdown")

# -------------------- GRANT COMMAND (TUZATILDI) --------------------
async def grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗️ Ishlatish: `/grant @username [son]`", parse_mode="Markdown")
        return
    
    target = args[0].replace("@", "").strip()
    count = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 1
    
    db = SessionLocal()
    # ID yoki Username bo'yicha izlash (katta-kichik harfga qaraysiz)
    if target.isdigit():
        user = db.query(User).filter_by(user_id=int(target)).first()
    else:
        user = db.query(User).filter(User.username.ilike(target)).first()
        
    if not user:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi")
        db.close()
        return
        
    user.tests_remaining += count
    user.access_granted_at = datetime.now()
    db.commit()
    
    display_name = f"@{user.username}" if user.username else f"ID: {user.user_id}"
    await update.message.reply_text(f"✅ {display_name} ga {count} ta test berildi!")
    db.close()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi")
    context.user_data.clear()
    return ConversationHandler.END

# -------------------- MAIN --------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    add_conv = ConversationHandler(
        entry_points=[
            CommandHandler("add_question", add_question_start),
            CallbackQueryHandler(add_question_start, pattern="^btn_add_q$")
        ],
        states={
            ASK_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_text)],
            ASK_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_a)],
            ASK_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_b)],
            ASK_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_c)],
            ASK_D: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_d)],
            ASK_CORRECT: [CallbackQueryHandler(ask_correct_button, pattern="^ans_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("grant", grant))
    app.add_handler(add_conv)
    app.add_handler(CallbackQueryHandler(edit_info_callback, pattern="^edit_info_"))
    app.add_handler(CallbackQueryHandler(admin_callback_handler))

    app.run_polling()

if __name__ == "__main__":
    main()