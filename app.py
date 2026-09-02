import os, logging, asyncio, threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from sqlalchemy import func
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from database import SessionLocal, User, Block, Question, UserAnswer, TestResult

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_IDS = [int(i.strip()) for i in os.environ.get('ADMIN_ID', '5690099705,6106446622').split(',') if i.strip()]
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

REG_NAME, REG_PHONE = range(2)

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

logging.basicConfig(level=logging.INFO)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# -------------------- TELEGRAM BOT LOGIKASI --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    if not user or not user.is_registered:
        if not user:
            user = User(user_id=user_id, username=update.effective_user.username)
            db.add(user)
            db.commit()
        db.close()
        await update.message.reply_text("Assalomu alaykum! Testni boshlashdan oldin ism va familiyangizni kiriting:")
        return REG_NAME

    db.close()
    await show_main_menu(update, user)
    return ConversationHandler.END

async def reg_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text.strip()
    contact_btn = KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
    keyboard = ReplyKeyboardMarkup([[contact_btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Rahmat! Endi pastdagi tugma orqali telefon raqamingizni yuboring:", reply_markup=keyboard)
    return REG_PHONE

async def reg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    contact = update.message.contact
    phone = contact.phone_number if contact else update.message.text.strip()

    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if user:
        user.full_name = context.user_data.get('full_name')
        user.phone_number = phone
        user.is_registered = True
        db.commit()
    db.close()

    await update.message.reply_text("✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", reply_markup=ReplyKeyboardRemove())
    await show_main_menu(update, user)
    return ConversationHandler.END

async def show_main_menu(update: Update, user):
    buttons = [[InlineKeyboardButton("📝 Test topshirish", web_app={"url": WEBAPP_URL})]]
    if is_admin(update.effective_user.id):
        buttons.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    msg_text = (
        f"Xush kelibsiz, {user.full_name or 'Foydalanuvchi'}!\n"
        f"📞 Tel: {user.phone_number or 'Kiritilmagan'}\n"
        f"📊 Qolgan imkoniyatlar: {user.tests_remaining}"
    )
    if update.message:
        await update.message.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(buttons))
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(buttons))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi Blok Yaratish", callback_data="btn_auto_add_block")],
        [InlineKeyboardButton("📋 Savollarni Ko'rish (< >)", callback_data="btn_view_q_0")]
    ])
    text = "🛠 **Admin Boshqaruv Paneli**"
    if query:
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def auto_add_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    count = db.query(Block).count()
    new_block = Block(title=f"{count + 1}-Blok")
    db.add(new_block)
    db.commit()
    title = new_block.title
    db.close()
    await query.message.reply_text(f"✅ Yangi `{title}` yaratildi!", parse_mode="Markdown")

async def view_questions_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[-1])

    db = SessionLocal()
    total_q = db.query(Question).count()
    q = db.query(Question).order_by(Question.id.asc()).offset(page).first()

    if not q:
        await query.message.edit_text("📋 Bazada savollar yo'q.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]]))
        db.close()
        return

    text = f"❓ **Savol {page + 1}/{total_q}** ({q.block.title})\n"
    text += f"📌 Turi: {'Variantli' if q.q_type == 'mcq' else 'Ochiq test'}\n\n"
    text += f"**Matn:** {q.text}\n"
    if q.q_type == 'mcq':
        text += f"A) {q.option_a}\nB) {q.option_b}\nC) {q.option_c}\nD) {q.option_d}\n"
    text += f"\n✅ **To'g'ri javob:** `{q.correct_answer}`"

    nav = []
    if page > 0: nav.append(InlineKeyboardButton("◀️ Oldingi", callback_data=f"btn_view_q_{page - 1}"))
    if page < total_q - 1: nav.append(InlineKeyboardButton("Keyingi ▶️", callback_data=f"btn_view_q_{page + 1}"))

    kb = InlineKeyboardMarkup([nav, [InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")]])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    db.close()

# -------------------- FLASK API ROUTELARI --------------------
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html') or send_from_directory('.', 'index.html')

@app.route('/api/user/profile')
def get_user_profile():
    user_id = request.args.get('user_id', type=int)
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            return jsonify({"error": "User topilmadi"}), 404

        last_res = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).first()
        total_tests = db.query(TestResult).filter_by(user_id=user_id).count()

        return jsonify({
            "full_name": user.full_name or "Noma'lum",
            "username": user.username or "-",
            "tests_remaining": user.tests_remaining,
            "total_tests_taken": total_tests,
            "last_result": {
                "correct": last_res.correct_answers,
                "wrong": last_res.wrong_answers,
                "percentage": last_res.percentage,
                "date": last_res.completed_at.strftime("%Y-%m-%d %H:%M")
            } if last_res else None
        })
    finally:
        db.close()

@app.route('/api/user/results')
def get_user_results():
    user_id = request.args.get('user_id', type=int)
    db = SessionLocal()
    try:
        results = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).all()
        return jsonify([{
            "correct": r.correct_answers,
            "wrong": r.wrong_answers,
            "percentage": r.percentage,
            "date": r.completed_at.strftime("%d.%m.%Y %H:%M")
        } for r in results])
    finally:
        db.close()

@app.route('/api/init')
def init_test():
    user_id = request.args.get('user_id', type=int)
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user or user.tests_remaining <= 0:
            return jsonify({"error": "Sizda test topshirish huquqi qolmagan!"}), 403

        block = db.query(Block).order_by(Block.id.desc()).first()
        if not block:
            return jsonify({"error": "Hali blok va savollar yaratilmagan"}), 400

        questions = db.query(Question).filter_by(block_id=block.id).all()
        if not questions:
            return jsonify({"error": "Ushbu blokda savollar mavjud emas"}), 400

        db.query(UserAnswer).filter_by(user_id=user_id).delete()
        db.commit()

        q_data = []
        for q in questions:
            ua = UserAnswer(user_id=user_id, question_id=q.id)
            db.add(ua)
            q_data.append({
                "id": q.id,
                "q_type": q.q_type,
                "text": q.text,
                "options": [q.option_a, q.option_b, q.option_c, q.option_d] if q.q_type == 'mcq' else []
            })
        db.commit()

        return jsonify({"block_title": block.title, "questions": q_data})
    finally:
        db.close()

@app.route('/api/save', methods=['POST'])
def save_answer():
    data = request.json or {}
    user_id = data.get('user_id')
    q_id = data.get('question_id')
    val = data.get('selected_option')

    db = SessionLocal()
    try:
        ua = db.query(UserAnswer).filter_by(user_id=user_id, question_id=q_id).first()
        if ua:
            ua.user_answer = str(val).strip()
            db.commit()
        return jsonify({"status": "ok"})
    finally:
        db.close()

@app.route('/api/finish', methods=['POST'])
def finish_test():
    data = request.json or {}
    user_id = data.get('user_id')

    db = SessionLocal()
    try:
        user_answers = db.query(UserAnswer).filter_by(user_id=user_id).all()
        correct, wrong = 0, 0

        for ua in user_answers:
            q = db.query(Question).filter_by(id=ua.question_id).first()
            if not q or not ua.user_answer:
                wrong += 1
                continue

            user_val = str(ua.user_answer).strip()
            correct_val = str(q.correct_answer).strip()

            if q.q_type == 'open':
                is_correct = (user_val.lower() == correct_val.lower())
            else:
                is_correct = (user_val.upper() == correct_val.upper())

            ua.is_correct = is_correct
            if is_correct: correct += 1
            else: wrong += 1

        total = correct + wrong
        percentage = int((correct / total) * 100) if total > 0 else 0

        res = TestResult(user_id=user_id, total_questions=total, correct_answers=correct, wrong_answers=wrong, percentage=percentage)
        db.add(res)

        user = db.query(User).filter_by(user_id=user_id).first()
        if user and user.tests_remaining > 0:
            user.tests_remaining -= 1

        db.commit()
        return jsonify({"correct": correct, "wrong": wrong, "percentage": percentage})
    finally:
        db.close()

# -------------------- BOTNI ISHLATISH --------------------
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), reg_phone)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(auto_add_block, pattern="^btn_auto_add_block$"))
    application.add_handler(CallbackQueryHandler(view_questions_pagination, pattern="^btn_view_q_"))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)