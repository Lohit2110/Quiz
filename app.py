from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
import os
import sqlite3
import json
import time
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage

# ========== CONFIG ==========
app = Flask(__name__)
app.secret_key = 'quiz_secret_key'
UPLOAD_FOLDER = 'static/uploads'
QUIZ_FOLDER = 'quizzes'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QUIZ_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ========== DATABASE SETUP ==========
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY,
            question TEXT,
            q_img TEXT,
            opt_a TEXT, opt_b TEXT, opt_c TEXT, opt_d TEXT,
            correct TEXT,
            marks INTEGER
        )''')

# ========== ROUTES ==========

# Route to delete a quiz file
@app.route('/delete_quiz', methods=['POST'])
def delete_quiz():
    quiz_name = request.form.get('quiz_name')
    if quiz_name:
        quiz_path = os.path.join(QUIZ_FOLDER, quiz_name)
        if os.path.exists(quiz_path):
            os.remove(quiz_path)
    return redirect(url_for('index'))

@app.route('/')
def index():
    quiz_files = [f for f in os.listdir(QUIZ_FOLDER) if f.endswith('.json')]
    return render_template('index.html', quiz_files=quiz_files)

@app.route('/rename_quiz', methods=['POST'])
def rename_quiz():
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')

    if old_name and new_name:
        if not new_name.endswith('.json'):
            new_name += '.json'
        old_path = os.path.join(QUIZ_FOLDER, old_name)
        new_path = os.path.join(QUIZ_FOLDER, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
    return redirect(url_for('index'))

@app.route('/make_quiz', methods=['POST'])
def make_quiz():
    num_q = int(request.form.get('num_questions', 0))
    return render_template('create_quiz.html', num_questions=num_q, edit_mode=False) if num_q > 0 else redirect(url_for('index'))

@app.route('/edit_quiz/<quiz_file>')
def edit_quiz(quiz_file):
    with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Process each question to ensure image URLs are properly set
    for question in questions:
        if question['qtype'] == 'image' and question.get('q_img'):
            # Make sure the image path is relative to static folder
            question['image_url'] = '/' + question['q_img']
    
    return render_template('create_quiz.html', num_questions=len(questions), 
                         edit_mode=True, questions=questions, quiz_file=quiz_file)

@app.route('/save_quiz', methods=['POST'])
def save_quiz():
    num_questions = int(request.form['num_questions'])
    quiz_data = []
    existing_quiz = request.form.get('existing_quiz')

    for i in range(num_questions):
        q_type = request.form.get(f'qtype_{i}')
        question = request.form.get(f'qtext_{i}') if q_type == 'text' else ''
        img_path = ''

        # Check for existing image first
        existing_image = request.form.get(f'existing_image_{i}')
        if existing_image and existing_image.strip() and q_type == 'image':
            # Remove the leading slash if present
            img_path = existing_image.lstrip('/')
        else:
            # Handle new image upload
            q_img_file = request.files.get(f'qimg_{i}')
            if q_img_file and q_type == 'image' and q_img_file.filename:
                # Ensure we have a valid filename and content type
                filename = secure_filename(q_img_file.filename)
                ext = os.path.splitext(filename)[1].lower() or '.png'
                if not ext.startswith('.'):
                    ext = '.' + ext
                
                # Generate unique filename
                unique_name = f"qimg_{int(time.time() * 1000)}_{i}{ext}"
                full_img_path = os.path.join(UPLOAD_FOLDER, unique_name)
                
                # Save the file
                q_img_file.save(full_img_path)
                img_path = f"{UPLOAD_FOLDER}/{unique_name}"

        marks = int(request.form.get(f'marks_{i}', 0) or 0)

        quiz_data.append({
            'qtype': q_type,
            'question': question,
            'q_img': img_path,
            'opt_a': request.form.get(f'opt_a_{i}'),
            'opt_b': request.form.get(f'opt_b_{i}'),
            'opt_c': request.form.get(f'opt_c_{i}'),
            'opt_d': request.form.get(f'opt_d_{i}'),
            'correct': request.form.get(f'correct_{i}'),
            'marks': marks
        })

    if existing_quiz:
        filename = existing_quiz
    else:
        filename = f"quiz_{int(time.time())}.json"
        
    with open(os.path.join(QUIZ_FOLDER, filename), 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, ensure_ascii=False, indent=2)

    return redirect(url_for('index'))

@app.route('/quizzes/<quiz_file>')
def take_quiz(quiz_file):
    time_limit = request.args.get('time_limit', default=30, type=int)  # Default 30 minutes
    with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Initialize session for this quiz
    session['quiz_file'] = quiz_file
    session['time_limit'] = time_limit
    session['total_questions'] = len(questions)
    session['quiz_answers'] = {}  # Store answers as user progresses
    
    # Redirect to first question
    return redirect(url_for('quiz_question', quiz_file=quiz_file, question_num=1))

@app.route('/quizzes/<quiz_file>/question/<int:question_num>')
def quiz_question(quiz_file, question_num):
    # Load quiz data
    with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Validate question number
    if question_num < 1 or question_num > len(questions):
        return redirect(url_for('take_quiz', quiz_file=quiz_file))
    
    # Get current question (adjust for 0-based indexing)
    current_question = questions[question_num - 1]
    
    # Get session data
    time_limit = session.get('time_limit', 30)
    total_questions = len(questions)
    quiz_answers = session.get('quiz_answers', {})
    
    return render_template('quiz_question.html', 
                         question=current_question,
                         question_num=question_num,
                         total_questions=total_questions,
                         quiz_file=quiz_file,
                         time_limit=time_limit,
                         current_answer=quiz_answers.get(str(question_num - 1), ''))

@app.route('/save_answer', methods=['POST'])
def save_answer():
    quiz_file = request.form.get('quiz_file')
    question_num = int(request.form.get('question_num'))
    answer = request.form.get('answer', '')
    action = request.form.get('action')  # 'next', 'previous', or 'submit'
    
    # Initialize quiz_answers if not exists
    if 'quiz_answers' not in session:
        session['quiz_answers'] = {}
    
    # Save the answer (adjust for 0-based indexing)
    session['quiz_answers'][str(question_num - 1)] = answer
    session.modified = True
    
    # Load quiz to get total questions
    with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    total_questions = len(questions)
    
    # Handle navigation
    if action == 'next' and question_num < total_questions:
        return redirect(url_for('quiz_question', quiz_file=quiz_file, question_num=question_num + 1))
    elif action == 'previous' and question_num > 1:
        return redirect(url_for('quiz_question', quiz_file=quiz_file, question_num=question_num - 1))
    elif action == 'submit':
        return redirect(url_for('submit_paginated_quiz'))
    else:
        # If at last question and clicking next, go to submit
        if question_num == total_questions:
            return redirect(url_for('submit_paginated_quiz'))
        else:
            return redirect(url_for('quiz_question', quiz_file=quiz_file, question_num=question_num))

@app.route('/submit_paginated_quiz')
def submit_paginated_quiz():
    quiz_file = session.get('quiz_file')
    quiz_answers = session.get('quiz_answers', {})
    
    if not quiz_file:
        return redirect(url_for('index'))
    
    # Load quiz questions
    with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Calculate score
    score = 0
    total_questions = len(questions)
    answered_questions = []
    
    for i, q in enumerate(questions):
        user_answer = quiz_answers.get(str(i), '').strip().upper()
        correct_answer = str(q['correct']).strip().upper()
        
        # Handle unanswered questions
        if user_answer == '':
            marks = 0
            is_correct = False
        else:
            is_correct = user_answer == correct_answer
            marks = 4 if is_correct else -1
        
        score += marks
        
        answered_questions.append({
            'index': i + 1,
            'question': q.get('question', ''),
            'q_img': q.get('q_img', ''),
            'correct': q['correct'],
            'user_answer': user_answer,
            'is_correct': is_correct,
            'marks_obtained': marks,
            'opt_a': q.get('opt_a', ''),
            'opt_b': q.get('opt_b', ''),
            'opt_c': q.get('opt_c', ''),
            'opt_d': q.get('opt_d', '')
        })
    
    max_score = total_questions * 4
    
    # Store results in session for PDF download
    session['score'] = score
    session['max_score'] = max_score
    session['answered_questions'] = answered_questions
    
    # Clear quiz session data
    session.pop('quiz_file', None)
    session.pop('quiz_answers', None)
    session.pop('time_limit', None)
    session.pop('total_questions', None)
    session.modified = True
    
    return render_template('result.html', 
                        score=score, 
                        max_score=max_score,
                        answered_questions=answered_questions,
                        total_questions=total_questions,
                        quiz_file=quiz_file)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    score = 0
    total_questions = 0
    answered_questions = []

    if request.form.get('from_file') == '1':
        quiz_file = request.form.get('quiz_file')
        with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
            questions = json.load(f)

        for i, q in enumerate(questions):
            total_questions += 1
            user_answer = request.form.get(f'q_{i}', '')  # Get raw answer, might be None if unanswered
            
            # Process answers and calculate marks
            correct_answer = str(q['correct']).strip().upper()
            
            # Handle unanswered questions
            if user_answer is None or user_answer.strip() == '':
                marks = 0
                user_answer = ''
                is_correct = False
            else:
                user_answer = user_answer.strip().upper()
                is_correct = user_answer == correct_answer
                marks = 4 if is_correct else -1
            
            score += marks

            answered_questions.append({
                'index': i + 1,
                'question': q.get('question', ''),
                'q_img': q.get('q_img', ''),
                'correct': q['correct'],
                'user_answer': user_answer,
                'is_correct': is_correct,
                'marks_obtained': marks,
                'opt_a': q.get('opt_a', ''),
                'opt_b': q.get('opt_b', ''),
                'opt_c': q.get('opt_c', ''),
                'opt_d': q.get('opt_d', '')
                })

        max_score = total_questions * 4
        
        # Store results in session for PDF download
        session['score'] = score
        session['max_score'] = max_score
        session['answered_questions'] = answered_questions
        
        return render_template('result.html', 
                            score=score, 
                            max_score=max_score,
                            answered_questions=answered_questions,
                            total_questions=total_questions,
                            quiz_file=quiz_file)

    # If quiz is from DB
    with sqlite3.connect('database.db') as conn:
        data = conn.execute('SELECT id, correct, marks FROM quizzes').fetchall()

    for q_id, correct, marks in data:
        user_answer = request.form.get(f'q_{q_id}', '').strip().upper()
        if user_answer == str(correct).strip().upper():
            score += marks

    return render_template('result.html', score=score)

@app.route('/download_quiz_pdf/<quiz_file>')
def download_quiz_pdf(quiz_file):
    # Read quiz data
    with open(os.path.join(QUIZ_FOLDER, quiz_file), 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    question_style = ParagraphStyle(
        'CustomQuestion',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        spaceBefore=16
    )
    
    option_style = ParagraphStyle(
        'CustomOption',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=6
    )
    
    # Add title
    title = Paragraph(f"Quiz: {quiz_file}", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Add questions
    for i, q in enumerate(questions, 1):
        # Question text
        question_text = f"Question {i}: {q.get('question', '')}"
        story.append(Paragraph(question_text, question_style))
        
        # Add image if present
        img_path = q.get('q_img', '')
        if img_path and os.path.exists(img_path):
            try:
                # Open image with PIL to get dimensions
                img = PILImage.open(img_path)
                w, h = img.size
                # Scale image to fit page width while maintaining aspect ratio
                aspect = h / float(w)
                max_width = 6 * inch  # Maximum width (leaving margins)
                width = min(w, max_width)
                height = width * aspect
                
                # Create ReportLab image
                img = Image(img_path, width=width, height=height)
                img.hAlign = 'CENTER'  # Center the image
                story.append(Spacer(1, 12))
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception as e:
                # If image processing fails, add a placeholder text
                story.append(Paragraph(f"[Image could not be loaded: {os.path.basename(img_path)}]", styles['Italic']))
        
        # Options
        options = [
            ('A', q.get('opt_a', '')),
            ('B', q.get('opt_b', '')),
            ('C', q.get('opt_c', '')),
            ('D', q.get('opt_d', ''))
        ]
        
        for opt, text in options:
            option_text = f"{opt}. {text}"
            story.append(Paragraph(option_text, option_style))
        
        # Add marks
        marks_text = f"Marks: {q.get('marks', 4)}"
        story.append(Paragraph(marks_text, styles['Italic']))
        story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"quiz_{quiz_file.replace('.json', '')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/download_result_pdf')
def download_result_pdf():
    # Get quiz results from session
    score = session.get('score', 0)
    max_score = session.get('max_score', 0)
    answered_questions = session.get('answered_questions', [])
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    # Add title
    title = Paragraph("Quiz Results", title_style)
    story.append(title)
    
    # Add summary
    summary_data = [
        ['Total Score:', f"{score} out of {max_score}"],
        ['Correct Answers:', str(len([q for q in answered_questions if q['is_correct']]))],
        ['Wrong Answers:', str(len([q for q in answered_questions if not q['is_correct'] and q['user_answer']]))],
        ['Unanswered:', str(len([q for q in answered_questions if not q['user_answer']]))]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Add detailed results
    for i, q in enumerate(answered_questions, 1):
        # Create a result header with background color based on answer status
        if q['is_correct']:
            bg_color = colors.Color(0.9, 1, 0.9)  # Light green
        elif not q['user_answer']:
            bg_color = colors.Color(1, 1, 0.9)    # Light yellow
        else:
            bg_color = colors.Color(1, 0.9, 0.9)  # Light red
            
        header_style = ParagraphStyle(
            'ResultHeader',
            parent=styles['Heading2'],
            backColor=bg_color,
            borderColor=colors.black,
            borderWidth=1,
            borderPadding=10,
            spaceAfter=15
        )
        
        # Question header with number and status
        question_text = f"Question {i}: {q.get('question', '')}"
        story.append(Paragraph(question_text, header_style))
        
        # Add image if present
        img_path = q.get('q_img', '')
        if img_path and os.path.exists(img_path):
            try:
                # Open image with PIL to get dimensions
                img = PILImage.open(img_path)
                w, h = img.size
                # Scale image to fit page width while maintaining aspect ratio
                aspect = h / float(w)
                max_width = 6 * inch  # Maximum width (leaving margins)
                width = min(w, max_width)
                height = width * aspect
                
                # Create ReportLab image
                img = Image(img_path, width=width, height=height)
                img.hAlign = 'CENTER'  # Center the image
                story.append(Spacer(1, 12))
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception as e:
                # If image processing fails, add a placeholder text
                story.append(Paragraph(f"[Image could not be loaded: {os.path.basename(img_path)}]", styles['Italic']))
        
        # Answer details in a table format
        answer_data = [
            ['Your Answer:', q.get('user_answer', 'Not answered')],
            ['Correct Answer:', q.get('correct', '')],
            ['Points:', f"{'+4' if q['is_correct'] else '0' if not q['user_answer'] else '-1'}"]
        ]
        
        answer_table = Table(answer_data, colWidths=[2*inch, 4*inch])
        answer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        story.append(answer_table)
        story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name="quiz_results.pdf",
        mimetype='application/pdf'
    )

# ========== MAIN ==========
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

