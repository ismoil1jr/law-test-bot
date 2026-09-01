from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from database import SessionLocal, User, Question, UserAnswer, TestResult
import random
import os

# -------------------- KONFIGURATSIYA --------------------
BOT_TOKEN = os.environ.get('BOT_TOKEN', "8840031160:AAFFVOrr_aK0LBGPYX2lAEBkcmkpMDauXKY")
ADMIN_ID = int(os.environ.get('ADMIN_ID', 5690099705))
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', "erkinvv17")
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

app = Flask(__name__)
CORS(app)

# ❌ Bot import va thread YO'Q!

# -------------------- STATIC FAYLLAR --------------------
@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_file(os.path.join('static', path))

# -------------------- USER PROFILE --------------------
@app.route('/api/user/profile')
def user_profile():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400
    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user:
        db.close()
        return jsonify({"error": "Foydalanuvchi topilmadi"}), 404
    results_count = db.query(TestResult).filter_by(user_id=user_id).count()
    last = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).first()
    db.close()
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

# -------------------- USER RESULTS HISTORY --------------------
@app.route('/api/user/results')
def user_results():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400
    db = SessionLocal()
    results = db.query(TestResult).filter_by(user_id=user_id).order_by(TestResult.completed_at.desc()).all()
    data = [{
        "id": r.id,
        "total": r.total_questions,
        "correct": r.correct_answers,
        "wrong": r.wrong_answers,
        "percentage": r.percentage,
        "date": r.completed_at.strftime('%d.%m.%Y %H:%M')
    } for r in results]
    db.close()
    return jsonify(data)

# -------------------- TEST INIT --------------------
@app.route('/api/init')
def init_test():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400

    db = SessionLocal()
    user = db.query(User).filter_by(user_id=user_id).first()
    if not user or user.tests_remaining <= 0:
        db.close()
        return jsonify({"error": "Sizda test huquqi yo'q"}), 403

    questions = db.query(Question).all()
    if len(questions) < 30:
        db.close()
        return jsonify({"error": f"Hali 30 ta savol qo'shilmagan! (hozir {len(questions)})"}), 400

    selected = random.sample(questions, 30)

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
    db.close()
    return jsonify({"questions": result})

# -------------------- SAVE ANSWER --------------------
@app.route('/api/save', methods=['POST'])
def save_answer():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    selected_option = data.get('selected_option')

    db = SessionLocal()
    ua = db.query(UserAnswer).filter_by(user_id=user_id, question_id=question_id).first()
    if not ua:
        db.close()
        return jsonify({"error": "Savol topilmadi"}), 404

    q = db.query(Question).filter_by(id=question_id).first()
    is_correct = (selected_option == q.correct_answer)
    ua.selected_option = selected_option
    ua.is_correct = is_correct
    ua.updated_at = datetime.now()
    db.commit()
    db.close()
    return jsonify({"status": "ok"})

# -------------------- FINISH TEST --------------------
@app.route('/api/finish', methods=['POST'])
def finish_test():
    data = request.json
    user_id = data.get('user_id')

    db = SessionLocal()
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

    details = []
    for a in answers:
        q = db.query(Question).filter_by(id=a.question_id).first()
        details.append({
            "question": q.text,
            "your_answer": a.selected_option,
            "correct_answer": q.correct_answer,
            "is_correct": a.is_correct
        })

    db.close()
    return jsonify({
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "percentage": percentage,
        "details": details
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
