# Quiz Web Application

A Flask-based quiz application that allows users to create, edit, and take quizzes with support for text and image questions.

## Features

- Create quizzes with text and image questions
- Edit existing quizzes
- Take quizzes with time limits
- View detailed results
- Download quiz and results as PDF
- Support for multiple choice questions (A, B, C, D)
- Scoring system: +4 for correct answers, -1 for wrong answers, 0 for unanswered

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application at `http://localhost:5000`

## Deployment

This application is configured for deployment on Render with:
- `Procfile` for web server configuration
- `requirements.txt` for Python dependencies
- Production-ready Flask settings

## File Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/uploads/` - Uploaded images
- `quizzes/` - Stored quiz JSON files
- `database.db` - SQLite database
