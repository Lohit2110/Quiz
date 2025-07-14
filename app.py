from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import sqlite3
import json
import time

app = Flask(__name__)
app.secret_key = 'quiz_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes
                 (id INTEGER PRIMARY KEY, question TEXT, q_img TEXT, opt_a TEXT, opt_b TEXT, opt_c TEXT, opt_d TEXT, correct TEXT, marks INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    quiz_files = []
    if os.path.exists('quizzes'):
        quiz_files = [f for f in os.listdir('quizzes') if f.endswith('.json')]
    return render_template('index.html', quiz_files=quiz_files)

# Route to rename a quiz file
@app.route('/rename_quiz', methods=['POST'])
def rename_quiz():
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    if not old_name or not new_name:
        return redirect('/')
    # Ensure .json extension
    if not new_name.endswith('.json'):
        new_name += '.json'
    old_path = os.path.join('quizzes', old_name)
    new_path = os.path.join('quizzes', new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
    return redirect('/')

@app.route('/make_quiz', methods=['GET', 'POST'])
def make_quiz():
    if request.method == 'POST':
        num_q = int(request.form['num_questions'])
        return render_template('create_quiz.html', num_questions=num_q)
    return redirect('/')

@app.route('/save_quiz', methods=['POST'])
def save_quiz():
    # Ensure quizzes directory exists
    os.makedirs('quizzes', exist_ok=True)
    num_questions = int(request.form['num_questions'])
    quiz_data = []
    for i in range(num_questions):
        q_type = request.form.get(f'qtype_{i}')
        question = request.form.get(f'qtext_{i}') if q_type == 'text' else ''
        q_img_file = request.files.get(f'qimg_{i}')

        img_path = ''
        if q_img_file and q_type == 'image':
            filename = secure_filename(q_img_file.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            q_img_file.save(img_path)

        opt_a = request.form.get(f'opt_a_{i}')
        opt_b = request.form.get(f'opt_b_{i}')
        opt_c = request.form.get(f'opt_c_{i}')
        opt_d = request.form.get(f'opt_d_{i}')
        correct = request.form.get(f'correct_{i}')
        marks = int(request.form.get(f'marks_{i}'))

        quiz_data.append({
            'qtype': q_type,
            'question': question,
            'q_img': img_path,
            'opt_a': opt_a,
            'opt_b': opt_b,
            'opt_c': opt_c,
            'opt_d': opt_d,
            'correct': correct,
            'marks': marks
        })
    # Save to file with timestamp
    quiz_filename = f"quiz_{int(time.time())}.json"
    quiz_path = os.path.join('quizzes', quiz_filename)
    with open(quiz_path, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, ensure_ascii=False, indent=2)
    return redirect('/')

@app.route('/quizzes/<quiz_file>')
def take_quiz(quiz_file):
    # Ensure quizzes directory exists
    os.makedirs('quizzes', exist_ok=True)
    quiz_path = os.path.join('quizzes', quiz_file)
    with open(quiz_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    return render_template('quiz.html', questions=questions, from_file=True, quiz_file=quiz_file)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    # If quiz is from file, load questions from the file
    if request.form.get('from_file') == '1':
        quiz_file = request.form.get('quiz_file')
        quiz_path = os.path.join('quizzes', quiz_file)
        with open(quiz_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        score = 0
        for i, q in enumerate(questions):
            answer = request.form.get(f'q_{i}')
            if answer is not None and answer.strip().upper() == str(q['correct']).strip().upper():
                score += q['marks']
        return render_template('result.html', score=score)
    # ...existing code for DB quizzes...
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, correct, marks FROM quizzes')
    data = c.fetchall()
    conn.close()

    score = 0
    for q_id, correct, marks in data:
        answer = request.form.get(f'q_{q_id}')
        if answer is not None and answer.strip().upper() == str(correct).strip().upper():
            score += marks

    return render_template('result.html', score=score)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
