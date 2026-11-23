import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload folder ka path set karna
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 1. Database Setup (Table banana)
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            semester TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            filename TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 2. Home Page, Search aur File List dikhana
@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    sem_filter = request.args.get('semester', '')
   
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
   
    # Filter aur Search ke hisaab se data nikalna
    query = "SELECT * FROM study_materials WHERE 1=1"
    params = []
   
    if search_query:
        query += " AND (title LIKE ? OR subject LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
       
    if sem_filter:
        query += " AND semester = ?"
        params.append(sem_filter)
       
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    materials = cursor.fetchall()
    conn.close()
   
    return render_template('index.html', materials=materials, search_query=search_query, sem_filter=sem_filter)

# 3. File Upload Handle Karna
@app.route('/upload', methods=['POST'])
def upload_file():
    title = request.form['title']
    subject = request.form['subject']
    semester = request.form['semester']
    doc_type = request.form['doc_type']
    file = request.files['file']
   
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        # File ko uploads folder mein save karna
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       
        # Details ko database mein save karna
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO study_materials (title, subject, semester, doc_type, filename)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, subject, semester, doc_type, filename))
        conn.commit()
        conn.close()
       
    return redirect(url_for('index'))

# 4. File Download Karwana
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)