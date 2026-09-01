import os
import random
import logging
import threading
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sqlalchemy import func, or_

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from database import SessionLocal, User, TestResult, Question, UserAnswer

logging.basicConfig(level=logging.INFO)

# -------------------- KONFIGURATSIYA --------------------
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN o'rnatilmagan!")

ADMIN_IDS = [int(i.strip()) for i in os.environ.get('ADMIN_ID', '5690099705,6106446622').split(',') if i.strip()]
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

app = Flask(__name__)
CORS(app)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# -------------------- TELEGRAM BOT --------------------
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

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id if update.effective_user else update.callback_query.from_user.id
    if not is_admin(user_id):
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Baza statistikasi", callback_data="btn_stats_q")],
        [InlineKeyboardButton("🎁 Test berish qo'llanmasi", callback_data="btn_grant_info")]
    ])
    text = "🛠 **Admin Boshqaruv Paneli**\n\nKerakli bo'limni tanlang:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    if query.data == "admin_panel":
        await admin_panel(update, context)
    elif query.data == "btn_stats_q":
        db = SessionLocal()
        q_count = db.query(Question).count()
        u_count = db.query(User).count()
        r_count = db.query(TestResult).count()
        db.close()
        msg = f"📊 **Statistika:**\n\n👥 Foydalanuvchilar: {u_count} ta\n❓ Savollar: {q_count} ta\n📝 Yechilgan testlar: {r_count} ta"
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]])
        await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")
    elif query.data == "btn_grant_info":
        msg = "🎁 **Foydalanuvchiga test berish:**\n\nBuyruq shakli:\n`/grant @username 5`\nyoki ID bo'yicha:\n`/grant 12345678 5`"
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]])
        await query.message.edit_text(msg, reply_markup=back_btn, parse_mode="Markdown")

async def grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗️ Ishlatish:\n`/grant @username 5` yoki `/grant 12345678 5`", parse_mode="Markdown")
        return

    raw_target = args[0].strip()
    clean_target = raw_target.replace("@", "").strip()
    count = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 1

    db = SessionLocal()
    try:
        if clean_target.isdigit():
            user = db.query(User).filter(User.user_id == int(clean_target)).first()
        else:
            user = db.query(User).filter(
                or_(
                    func.lower(User.username) == clean_target.lower(),
                    func.lower(User.username) == f"@{clean_target.lower()}"
                )
            ).first()

        if not user:
            await update.message.reply_text(f"❌ Foydalanuvchi (`{raw_target}`) topilmadi.", parse_mode="Markdown")
            return

        user.tests_remaining += count
        user.access_granted_at = datetime.now()
        db.commit()

        display_name = f"@{user.username}" if user.username else f"ID: {user.user_id}"
        await update.message.reply_text(f"✅ {display_name} ga {count} ta test berildi!\n📊 Jami testlari: {user.tests_remaining}")
    finally:
        db.close()

# -------------------- FLASK API ENDPOINTLAR (WebApp Uchun) --------------------
@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_file(os.path.join('static', path))

@app.route('/api/user/profile')
def user_profile():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id, username="", full_name="Foydalanuvchi")
            db.add(user)
            db.commit()
        
        results_count = db.query(TestResult).filter_by(user_id=user_id).count()
        last = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).first()
        
        return jsonify({
            "user_id": user.user_id,
            "username": user.username,
            "full_name": user.full_name,
            "tests_remaining": user.tests_remaining,
            "total_tests_taken": results_count,
            "last_result": {
                "correct": last.correct_answers,
                "wrong": last.wrong_answers,
                "percentage": last.percentage,
                "date": last.completed_at.strftime('%d.%m.%Y %H:%M')
            } if last else None
        })
    finally:
        db.close()

@app.route('/api/user/results')
def user_results():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400
    
    db = SessionLocal()
    try:
        results = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).all()
        data = [{
            "id": r.id,
            "total": r.total_questions,
            "correct": r.correct_answers,
            "wrong": r.wrong_answers,
            "percentage": r.percentage,
            "date": r.completed_at.strftime('%d.%m.%Y %H:%M')
        } for r in results]
        return jsonify(data)
    finally:
        db.close()

@app.route('/api/init')
def init_test():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user or user.tests_remaining <= 0:
            return jsonify({"error": "Sizda test huquqi yo'q"}), 403
        
        questions = db.query(Question).all()
        if not questions:
            return jsonify({"error": "Bazada hali savollar mavjud emas!"}), 400
        
        sample_size = min(len(questions), 30)
        selected = random.sample(questions, sample_size)
        
        db.query(UserAnswer).filter_by(user_id=user_id).delete()
        db.commit()
        
        result = []
        for q in selected:
            ua = UserAnswer(user_id=user_id, question_id=q.id, selected_option=None, is_correct=None)
            db.add(ua)
            result.append({
                "id": q.id,
                "text": q.text,
                "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                "selected": None
            })
        db.commit()
        return jsonify({"questions": result})
    finally:
        db.close()

@app.route('/api/save', methods=['POST'])
def save_answer():
    data = request.json or {}
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')
    
    db = SessionLocal()
    try:
        ua = db.query(UserAnswer).filter_by(user_id=user_id, question_id=question_id).first()
        if not ua:
            return jsonify({"error": "Savol topilmadi"}), 404
        
        q = db.query(Question).filter_by(id=question_id).first()
        is_correct = (selected_option == q.correct_answer)
        ua.selected_option = selected_option
        ua.is_correct = is_correct
        ua.updated_at = datetime.now()
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
        answers = db.query(UserAnswer).filter_by(user_id=user_id).all()
        total = len(answers)
        correct = sum(1 for a in answers if a.is_correct is True)
        wrong = sum(1 for a in answers if a.is_correct is False)
        percentage = int((correct / total) * 100) if total > 0 else 0
        
        result = TestResult(
            user_id=user_id,
            total_questions=total,
            correct_answers=correct,
            wrong_answers=wrong,
            percentage=percentage
        )
        db.add(result)
        
        user = db.query(User).filter_by(user_id=user_id).first()
        if user and user.tests_remaining > 0:
            user.tests_remaining -= 1
            
        db.commit()
        return jsonify({"status": "ok", "correct": correct, "wrong": wrong, "percentage": percentage})
    finally:
        db.close()

# -------------------- BOTNI FONDA ISHGA TUSHIRISH --------------------
def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("grant", grant))
    application.add_handler(CallbackQueryHandler(admin_callback_handler))
    
    application.run_polling(drop_pending_updates=True)

# Bot va WebApp ni parallel ishlatish
bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)