from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from database import SessionLocal, User, Question, UserAnswer, TestResult
import random
import os

# -------------------- KONFIGURATSIYA --------------------
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_IDS = [int(i.strip()) for i in os.environ.get('ADMIN_ID', '5690099705,6106446622').split(',') if i.strip()]
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', "erkinvv17")
WEBAPP_URL = os.environ.get('WEBAPP_URL', "https://law-test-bot-production.up.railway.app")

app = Flask(__name__)
CORS(app)

# -------------------- STATIC --------------------
@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_file(os.path.join('static', path))

# -------------------- API ENDPOINTLAR --------------------
@app.route('/api/user/profile')
def user_profile():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id kerak"}), 400
    
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            # Agar foydalanuvchi bazada hali bo'lmasa, uni yaratamiz
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
        
        details = []
        for a in answers:
            q = db.query(Question).filter_by(id=a.question_id).first()
            if q:
                details.append({
                    "question": q.text,
                    "your_answer": a.selected_option,
                    "correct_answer": q.correct_answer,
                    "is_correct": a.is_correct
                })
        return jsonify({
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "percentage": percentage,
            "details": details
        })
    finally:
        db.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)