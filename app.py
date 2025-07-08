from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Table des références (nom modifié)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_refs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_number INTEGER,
            username TEXT,
            date TEXT
        )
    ''')

    # Pré-remplissage des utilisateurs
    users = [
        ('aa', 'aapass', 'user'),
        ('mi', 'mipass', 'user'),
        ('rm', 'adminpass', 'admin'),
        ('rf', 'rfpass', 'user'),
        ('li', 'lipass', 'user')
    ]

    for user in users:
        cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?)', user)

    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['role'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/list')
def list_refs():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM document_refs ORDER BY id DESC')
    refs = cursor.fetchall()
    conn.close()

    return render_template('list.html', refs=refs, role=session['role'])

@app.route('/new')
def new_ref():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(ref_number) FROM document_refs')
    max_ref = cursor.fetchone()[0]
    next_ref = (max_ref + 1) if max_ref else 2448

    cursor.execute('INSERT INTO document_refs (ref_number, username, date) VALUES (?, ?, ?)',
                   (next_ref, session['username'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

    return redirect(url_for('list_refs'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)
