import os, logging, asyncio, threading, random
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template
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
ADD_Q_TYPE, ADD_Q_TEXT, ADD_Q_A, ADD_Q_B, ADD_Q_C, ADD_Q_D, ADD_Q_CORRECT = range(2, 9)
EDIT_Q_TEXT, EDIT_Q_CORRECT = range(9, 11)

app = Flask(__name__, static_folder="static", template_folder="static")
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
    await show_main_menu(update, user.full_name, user.phone_number, user.tests_remaining)
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
        
        full_name = user.full_name
        phone_number = user.phone_number
        tests_remaining = user.tests_remaining
    db.close()

    await update.message.reply_text("✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", reply_markup=ReplyKeyboardRemove())
    await show_main_menu(update, full_name, phone_number, tests_remaining)
    return ConversationHandler.END

async def show_main_menu(update: Update, full_name, phone_number, tests_remaining):
    buttons = [[InlineKeyboardButton("📝 Test topshirish", web_app={"url": WEBAPP_URL})]]
    if is_admin(update.effective_user.id):
        buttons.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    msg_text = (
        f"Xush kelibsiz, {full_name or 'Foydalanuvchi'}!\n"
        f"📞 Tel: {phone_number or 'Kiritilmagan'}\n"
        f"📊 Qolgan imkoniyatlar: {tests_remaining}"
    )
    if update.message:
        await update.message.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(buttons))
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(buttons))

# --------------------- PLAN MENU ---------------------
async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⛔️ <b>Tizimda bepul testlar mavjud emas!</b>\n\n"
        "Siz hali test paketlarini sotib olmadingiz.\n"
        "Test imkoniyatlari va obuna narxlarini bilish hamda ularni xarid qilish uchun admin bilan bog'laning:\n\n"
        "👤 <b>Admin:</b> @qurbonov_oIimjon\n"
    )
    await update.message.reply_text(msg, parse_mode="HTML")

# -------------------- GRANT COMMAND --------------------
async def grant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ <b>Xato foydalanish!</b>\n\n"
            "Format: <code>/grant &lt;user_id yoki @username&gt; [soni]</code>\n"
            "Misol: <code>/grant 6106446622 2</code> yoki <code>/grant @qurbonov_oIimjon</code>",
            parse_mode="HTML"
        )
        return

    target = args[0].replace('@', '').strip()
    count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1

    db = SessionLocal()
    user = None
    if target.isdigit():
        user = db.query(User).filter_by(user_id=int(target)).first()
    else:
        user = db.query(User).filter(func.lower(User.username) == target.lower()).first()

    if not user:
        db.close()
        await update.message.reply_text("❌ Foydalanuvchi bazadan topilmadi!")
        return

    user.tests_remaining += count
    db.commit()
    new_count = user.tests_remaining
    db.close()

    await update.message.reply_text(
        f"✅ <b>{user.full_name or user.username or user.user_id}</b> ga {count} ta test imkoniyati berildi!\n"
        f"📊 Jami imkoniyati: <code>{new_count}</code> ta",
        parse_mode="HTML"
    )

# -------------------- ADMIN PANEL & USER MANAGEMENT --------------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query: await query.answer()

    if not is_admin(update.effective_user.id):
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yangi Blok Yaratish", callback_data="btn_auto_add_block")],
        [InlineKeyboardButton("📦 Bloklar va Savollar", callback_data="btn_list_blocks")],
        [InlineKeyboardButton("👥 Foydalanuvchilar Ro'yxati", callback_data="btn_admin_users_0")],
        [InlineKeyboardButton("📊 Umumiy Statistika", callback_data="btn_admin_stats")]
    ])
    text = "🛠 **Admin Boshqaruv Paneli**"
    if query:
        await query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update.effective_user.id): return

    parts = query.data.split("_")
    page = int(parts[3]) if len(parts) > 3 else 0
    per_page = 8

    db = SessionLocal()
    users = db.query(User).order_by(User.id.desc()).all()
    total_users = len(users)

    if not users:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")]])
        await query.message.edit_text("👥 Bazada foydalanuvchilar topilmadi.", reply_markup=kb)
        db.close()
        return

    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_users = users[start_idx:end_idx]

    buttons = []
    for u in page_users:
        name = u.full_name or (f"@{u.username}" if u.username else f"ID: {u.user_id}")
        buttons.append([InlineKeyboardButton(f"👤 {name} (Imkoniyat: {u.tests_remaining} ta)", callback_data=f"btn_user_detail_{u.user_id}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Oldingi", callback_data=f"btn_admin_users_{page - 1}"))
    if end_idx < total_users:
        nav.append(InlineKeyboardButton("Keyingi ▶️", callback_data=f"btn_admin_users_{page + 1}"))

    if nav: buttons.append(nav)
    buttons.append([InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")])
    db.close()

    text = f"👥 **Foydalanuvchilar ro'yxati** ({start_idx + 1}-{min(end_idx, total_users)} / {total_users}):"
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def admin_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update.effective_user.id): return

    user_id = int(query.data.split("_")[-1])
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()

    if not user:
        db.close()
        await query.message.edit_text("❌ Foydalanuvchi topilmadi!")
        return

    results = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).limit(10).all()
    db.close()

    res_text = ""
    if results:
        for idx, r in enumerate(results, 1):
            date_str = r.completed_at.strftime("%d.%m.%Y %H:%M") if r.completed_at else "-"
            res_text += f"\n  {idx}. 📅 {date_str} | **{r.percentage}%** ({r.correct_answers} to'g'ri / {r.wrong_answers} xato)"
    else:
        res_text = "\n  *Hali birorta ham test topshirmagan.*"

    text = (
        f"👤 **Foydalanuvchi Profil:**\n\n"
        f"🆔 **Telegram ID:** `{user.user_id}`\n"
        f"📛 **Ism-familiya:** {user.full_name or 'Kiritilmagan'}\n"
        f"💬 **Username:** @{user.username if user.username else 'yoq'}\n"
        f"📞 **Telefon:** {user.phone_number or 'Kiritilmagan'}\n"
        f"📊 **Qolgan imkoniyati:** `{user.tests_remaining}` ta\n\n"
        f"📝 **Oxirgi test natijalari (Max 10 ta):**{res_text}"
    )

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ 1 ta imkoniyat", callback_data=f"btn_quick_grant_{user.user_id}_1"),
            InlineKeyboardButton("➕ 5 ta imkoniyat", callback_data=f"btn_quick_grant_{user.user_id}_5")
        ],
        [InlineKeyboardButton("⬅️ Foydalanuvchilar ro'yxatiga", callback_data="btn_admin_users_0")]
    ])

    await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

async def admin_quick_grant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update.effective_user.id): return

    parts = query.data.split("_")
    user_id = int(parts[3])
    count = int(parts[4])

    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if user:
        user.tests_remaining += count
        db.commit()
    db.close()

    await query.answer(f"✅ {count} ta imkoniyat berildi!", show_alert=True)
    await admin_user_detail(update, context)

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(update.effective_user.id): return

    db = SessionLocal()
    total_users = db.query(User).count()
    registered_users = db.query(User).filter_by(is_registered=True).count()
    total_tests = db.query(TestResult).count()
    db.close()

    stat_text = (
        "📊 **Foydalanuvchilar Statistikasi**\n\n"
        f"👤 Jami foydalanuvchilar: **{total_users}**\n"
        f"✅ Ro'yxatdan o'tganlar: **{registered_users}**\n"
        f"📝 Yakunlangan testlar: **{total_tests}**"
    )

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")]])
    await query.message.edit_text(stat_text, reply_markup=kb, parse_mode="Markdown")

# -------------------- BLOKLAR VA SAVOLLAR MANAGE --------------------
async def auto_add_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    db = SessionLocal()
    count = db.query(Block).count()
    new_block = Block(title=f"{count + 1}-Blok")
    db.add(new_block)
    db.commit()
    b_id = new_block.id
    title = new_block.title
    db.close()

    await query.message.reply_text(f"✅ Yangi `{title}` yaratildi!", parse_mode="Markdown")
    await show_block_detail(query, b_id)

async def list_blocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    blocks = db.query(Block).order_by(Block.id.asc()).all()

    if not blocks:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_panel")]])
        await query.message.edit_text("📦 Bazada hali bloklar mavjud emas.", reply_markup=kb)
        db.close()
        return

    buttons = []
    for b in blocks:
        q_cnt = db.query(Question).filter_by(block_id=b.id).count()
        buttons.append([InlineKeyboardButton(f"📦 {b.title} ({q_cnt}/45 savol)", callback_data=f"btn_block_{b.id}")])

    buttons.append([InlineKeyboardButton("⬅️ Admin Panel", callback_data="admin_panel")])
    db.close()

    await query.message.edit_text("📦 **Mavjud Bloklar:**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def block_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    block_id = int(query.data.split("_")[-1])
    await show_block_detail(query, block_id)

async def show_block_detail(query, block_id: int):
    db = SessionLocal()
    block = db.query(Block).filter_by(id=block_id).first()
    if not block:
        db.close()
        return

    mcq_cnt = db.query(Question).filter_by(block_id=block_id, q_type='mcq').count()
    open_cnt = db.query(Question).filter_by(block_id=block_id, q_type='open').count()
    total_cnt = mcq_cnt + open_cnt

    text = (
        f"📦 **{block.title}**\n\n"
        f"📊 Jami savollar: **{total_cnt}/45**\n"
        f"🔹 Variantli (MCQ): **{mcq_cnt}/35**\n"
        f"🔸 Ochiq test: **{open_cnt}/10**"
    )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Savol qo'shish", callback_data=f"btn_add_q_{block_id}")],
        [InlineKeyboardButton("📋 Savollarni ko'rish", callback_data=f"btn_view_bq_{block_id}_0")],
        [InlineKeyboardButton("🗑 Blokni o'chirish", callback_data=f"btn_del_block_{block_id}")],
        [InlineKeyboardButton("⬅️ Bloklar ro'yxatiga", callback_data="btn_list_blocks")]
    ])

    await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    db.close()

async def delete_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    block_id = int(query.data.split("_")[-1])

    db = SessionLocal()
    block = db.query(Block).filter_by(id=block_id).first()
    if block:
        db.delete(block)
        db.commit()
    db.close()

    await query.message.reply_text("✅ Blok va uning barcha savollari o'chirildi!")
    await list_blocks(update, context)

# -------------------- SAVOL QO'SHISH CONVERSATION --------------------
async def start_add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    block_id = int(query.data.split("_")[-1])
    context.user_data['target_block_id'] = block_id

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔹 Variantli test (MCQ)", callback_data="qtype_mcq")],
        [InlineKeyboardButton("🔸 Ochiq test (Open)", callback_data="qtype_open")]
    ])
    await query.message.reply_text("❓ **Savol turini tanlang:**", reply_markup=kb, parse_mode="Markdown")
    return ADD_Q_TYPE

async def select_q_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    q_type = "mcq" if query.data == "qtype_mcq" else "open"
    context.user_data['q_type'] = q_type

    await query.message.reply_text("📝 Savol matnini kiriting:")
    return ADD_Q_TEXT

async def input_q_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['q_text'] = update.message.text.strip()
    q_type = context.user_data.get('q_type')

    if q_type == 'mcq':
        await update.message.reply_text("A) Variant matnini kiriting:")
        return ADD_Q_A
    else:
        await update.message.reply_text("✅ To'g'ri javob matnini kiriting:")
        return ADD_Q_CORRECT

async def input_q_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['opt_a'] = update.message.text.strip()
    await update.message.reply_text("B) Variant matnini kiriting:")
    return ADD_Q_B

async def input_q_b(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['opt_b'] = update.message.text.strip()
    await update.message.reply_text("C) Variant matnini kiriting:")
    return ADD_Q_C

async def input_q_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['opt_c'] = update.message.text.strip()
    await update.message.reply_text("D) Variant matnini kiriting:")
    return ADD_Q_D

async def input_q_d(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['opt_d'] = update.message.text.strip()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("A", callback_data="ans_A"), InlineKeyboardButton("B", callback_data="ans_B")],
        [InlineKeyboardButton("C", callback_data="ans_C"), InlineKeyboardButton("D", callback_data="ans_D")]
    ])
    await update.message.reply_text("✅ To'g'ri javob qaysi variant?", reply_markup=kb)
    return ADD_Q_CORRECT

async def save_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_type = context.user_data.get('q_type')
    block_id = context.user_data.get('target_block_id')

    if q_type == 'mcq':
        query = update.callback_query
        await query.answer()
        correct_ans = query.data.split("_")[-1]
    else:
        correct_ans = update.message.text.strip()

    db = SessionLocal()
    new_q = Question(
        block_id=block_id,
        q_type=q_type,
        text=context.user_data.get('q_text'),
        option_a=context.user_data.get('opt_a'),
        option_b=context.user_data.get('opt_b'),
        option_c=context.user_data.get('opt_c'),
        option_d=context.user_data.get('opt_d'),
        correct_answer=correct_ans
    )
    db.add(new_q)
    db.commit()
    db.close()

    msg = update.callback_query.message if update.callback_query else update.message
    await msg.reply_text("✅ Savol muvaffaqiyatli saqlandi!")
    return ConversationHandler.END

# -------------------- SAVOLLARNI KO'RISH / TAHRIRLASH / O'CHIRISH --------------------
async def view_block_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    block_id = int(parts[3])
    page = int(parts[4])

    db = SessionLocal()
    questions = db.query(Question).filter_by(block_id=block_id).order_by(Question.id.asc()).all()
    total_q = len(questions)

    if not questions:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data=f"btn_block_{block_id}")]])
        await query.message.edit_text("📋 Ushbu blokda hali savollar mavjud emas.", reply_markup=kb)
        db.close()
        return

    q = questions[page]

    text = f"❓ **Savol {page + 1}/{total_q}**\n"
    text += f"📌 Turi: {'Variantli (MCQ)' if q.q_type == 'mcq' else 'Ochiq test'}\n\n"
    text += f"**Matn:** {q.text}\n"
    if q.q_type == 'mcq':
        text += f"A) {q.option_a}\nB) {q.option_b}\nC) {q.option_c}\nD) {q.option_d}\n"
    text += f"\n✅ **To'g'ri javob:** `{q.correct_answer}`"

    nav = []
    if page > 0: nav.append(InlineKeyboardButton("◀️ Oldingi", callback_data=f"btn_view_bq_{block_id}_{page - 1}"))
    if page < total_q - 1: nav.append(InlineKeyboardButton("Keyingi ▶️", callback_data=f"btn_view_bq_{block_id}_{page + 1}"))

    action_row = [
        InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"btn_edit_q_{q.id}"),
        InlineKeyboardButton("🗑 O'chirish", callback_data=f"btn_del_q_{q.id}_{block_id}")
    ]

    kb = InlineKeyboardMarkup([nav, action_row, [InlineKeyboardButton("⬅️ Blok menyusiga", callback_data=f"btn_block_{block_id}")]])
    await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    db.close()

async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    q_id = int(parts[3])
    block_id = int(parts[4])

    db = SessionLocal()
    q = db.query(Question).filter_by(id=q_id).first()
    if q:
        db.delete(q)
        db.commit()
    db.close()

    await query.message.reply_text("✅ Savol o'chirildi!")
    await show_block_detail(query, block_id)

async def start_edit_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    q_id = int(query.data.split("_")[-1])
    context.user_data['edit_q_id'] = q_id

    await query.message.reply_text("📝 Savolning yangi matnini kiriting:")
    return EDIT_Q_TEXT

async def input_edit_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['edit_text'] = update.message.text.strip()
    await update.message.reply_text("✅ Savolning yangi to'g'ri javobini kiriting:")
    return EDIT_Q_CORRECT

async def save_edit_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_id = context.user_data.get('edit_q_id')
    new_text = context.user_data.get('edit_text')
    new_ans = update.message.text.strip()

    db = SessionLocal()
    q = db.query(Question).filter_by(id=q_id).first()
    if q:
        q.text = new_text
        q.correct_answer = new_ans
        db.commit()
    db.close()

    await update.message.reply_text("✅ Savol muvaffaqiyatli yangilandi!")
    return ConversationHandler.END

# -------------------- FLASK API ROUTELARI --------------------

@app.route('/')
def index():
    return app.send_static_file('index.html')

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
            return jsonify({"error": "Sizda test topshirish huquqi qolmagan! Admin bilan bog'laning."}), 403

        mcq_questions = db.query(Question).filter_by(q_type='mcq').all()
        open_questions = db.query(Question).filter_by(q_type='open').all()

        if len(mcq_questions) < 35 or len(open_questions) < 10:
            return jsonify({
                "error": f"Bazada yetarlicha savol mavjud emas! Kamida 35 ta variantli va 10 ta ochiq savol bo'lishi kerak. (Mavjud: MCQ-{len(mcq_questions)}, Open-{len(open_questions)})"
            }), 400

        selected_mcq = random.sample(mcq_questions, 35)
        selected_open = random.sample(open_questions, 10)
        
        selected_questions = selected_mcq + selected_open
        random.shuffle(selected_questions)

        db.query(UserAnswer).filter_by(user_id=user_id).delete()
        db.commit()

        q_data = []
        for q in selected_questions:
            ua = UserAnswer(user_id=user_id, question_id=q.id)
            db.add(ua)
            q_data.append({
                "id": q.id,
                "q_type": q.q_type,
                "text": q.text,
                "options": [q.option_a, q.option_b, q.option_c, q.option_d] if q.q_type == 'mcq' else []
            })
        db.commit()

        return jsonify({"block_title": "Aralash Test Blok (45 ta savol)", "questions": q_data})
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
    
    user_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), reg_phone)],
        },
        fallbacks=[CommandHandler('start', start)],
        per_message=False
    )

    add_q_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_question, pattern="^btn_add_q_")],
        states={
            ADD_Q_TYPE: [CallbackQueryHandler(select_q_type, pattern="^qtype_")],
            ADD_Q_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_q_text)],
            ADD_Q_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_q_a)],
            ADD_Q_B: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_q_b)],
            ADD_Q_C: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_q_c)],
            ADD_Q_D: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_q_d)],
            ADD_Q_CORRECT: [
                CallbackQueryHandler(save_question, pattern="^ans_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_question)
            ],
        },
        fallbacks=[],
        per_message=False
    )

    edit_q_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_edit_question, pattern="^btn_edit_q_")],
        states={
            EDIT_Q_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_edit_text)],
            EDIT_Q_CORRECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edit_question)]
        },
        fallbacks=[],
        per_message=False
    )
    
    application.add_handler(user_conv)
    application.add_handler(add_q_conv)
    application.add_handler(edit_q_conv)

    application.add_handler(CommandHandler('grant', grant_command))
    application.add_handler(CommandHandler('plans', plans_command))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_users_list, pattern="^btn_admin_users_"))
    application.add_handler(CallbackQueryHandler(admin_user_detail, pattern="^btn_user_detail_"))
    application.add_handler(CallbackQueryHandler(admin_quick_grant, pattern="^btn_quick_grant_"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^btn_admin_stats$"))
    application.add_handler(CallbackQueryHandler(auto_add_block, pattern="^btn_auto_add_block$"))
    application.add_handler(CallbackQueryHandler(list_blocks, pattern="^btn_list_blocks$"))
    application.add_handler(CallbackQueryHandler(block_detail_callback, pattern="^btn_block_"))
    application.add_handler(CallbackQueryHandler(delete_block, pattern="^btn_del_block_"))
    application.add_handler(CallbackQueryHandler(view_block_questions, pattern="^btn_view_bq_"))
    application.add_handler(CallbackQueryHandler(delete_question, pattern="^btn_del_q_"))
    
    application.run_polling(drop_pending_updates=True, stop_signals=None)

# -------------------- BOT THREAD VA SERVERNI ISHGATUSHIRISH --------------------
def start_bot_thread():
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

start_bot_thread()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)