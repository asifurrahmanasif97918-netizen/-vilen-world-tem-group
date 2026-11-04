import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'vilen_world_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ডাটাবেস টেবিল তৈরি
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS facebook_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            page_id TEXT NOT NULL,
            page_token TEXT NOT NULL,
            auto_message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return "VÎLËŇ WØRLD TÊAM GRØUP - Server is Running!"

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'vilen123':
            session['admin_logged_in'] = True
            return redirect(url_for('facebook_automation'))
        else:
            error = "ভুল ইউজারনেম বা পাসওয়ার্ড!"
            
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <title>Admin Login</title>
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-box { background: #1e293b; padding: 30px; border-radius: 8px; width: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            input { width: 100%; padding: 10px; margin: 10px 0; background: #334155; border: none; color: #fff; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; background: #2563eb; color: #fff; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
            .error { color: #f87171; font-size: 14px; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2 style="margin-top:0; text-align:center;">অ্যাডমিন লগইন</h2>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            <form method="POST">
                <input type="text" name="username" placeholder="ইউজারনেম" required>
                <input type="password" name="password" placeholder="পাসওয়ার্ড" required>
                <button type="submit">লগইন করুন</button>
            </form>
        </div>
    </body>
    </html>
    """, error=error)

# --- ফেসবুক পেজ অটোমেশন (অ্যাডমিন) ---
@app.route('/facebook-automation', methods=['GET', 'POST'])
def facebook_automation():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    message = ""

    if request.method == 'POST':
        p_name = request.form.get('page_name')
        p_id = request.form.get('page_id')
        p_token = request.form.get('page_token')
        auto_msg = request.form.get('auto_message')

        if p_name:
            conn.execute('INSERT INTO facebook_pages (page_name, page_id, page_token, auto_message) VALUES (?, ?, ?, ?)',
                         (p_name, p_id, p_token, auto_msg))
            conn.commit()
            message = "ফেসবুক পেজ সফলভাবে যুক্ত হয়েছে!"

    pages = conn.execute('SELECT * FROM facebook_pages').fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <title>Facebook Automation - Admin</title>
        <style>
            body { font-family: Arial, sans-serif; background: #0f172a; color: #fff; padding: 20px; }
            .container { max-width: 600px; margin: auto; background: #1e293b; padding: 20px; border-radius: 8px; }
            input, textarea { width: 100%; padding: 10px; margin: 10px 0; background: #334155; border: none; color: #fff; border-radius: 4px; box-sizing: border-box; }
            button { background: #2563eb; color: #fff; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
            .msg { color: #4ade80; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>ফেসবুক পেজ অটোমেশন সেটআপ</h2>
            {% if message %}
                <div class="msg">{{ message }}</div>
            {% endif %}
            <form method="POST">
                <label>পেজের নাম:</label>
                <input type="text" name="page_name" required>
                <label>পেজ আইডি:</label>
                <input type="text" name="page_id" required>
                <label>পেজ অ্যাক্সেস টোকেন:</label>
                <input type="text" name="page_token" required>
                <label>অটো রিপ্লাই মেসেজ:</label>
                <textarea name="auto_message" rows="3" required></textarea>
                <button type="submit">পেজ সেভ করুন</button>
            </form>
            <hr style="margin: 20px 0; border-color: #334155;">
            <h3>সংযুক্ত পেজসমূহ:</h3>
            <ul>
                {% for page in pages %}
                    <li>{{ page['page_name'] }} (ID: {{ page['page_id'] }})</li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    """, message=message, pages=pages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
