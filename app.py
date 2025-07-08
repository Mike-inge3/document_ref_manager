from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret-key'

def init_db():
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS references (
            ref_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_number INTEGER,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        users = [
            ('aa', 'aapass', 0),
            ('mi', 'mipass', 0),
            ('rm', 'adminpass', 1),
            ('rf', 'rfpass', 0),
            ('li', 'lipass', 0)
        ]
        for u in users:
            c.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)", u)
        conn.commit()

init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("users.db") as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username=?", (username,))
            row = c.fetchone()
            if row and row[0] == password:
                session['user'] = username
                return redirect(url_for('dashboard'))
        return "Login failed"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/new')
def new_ref():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT MAX(ref_number) FROM references")
        last = c.fetchone()[0]
        next_num = 2448 if last is None else last + 1
        c.execute("INSERT INTO references (ref_number, created_by) VALUES (?, ?)", (next_num, session['user']))
        conn.commit()
    return render_template('new.html', ref=next_num)

@app.route('/list')
def list_refs():
    if 'user' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("users.db") as conn:
        c = conn.cursor()
        c.execute("SELECT ref_number, created_by, created_at FROM references ORDER BY ref_number DESC")
        data = c.fetchall()
    return render_template('list.html', data=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)