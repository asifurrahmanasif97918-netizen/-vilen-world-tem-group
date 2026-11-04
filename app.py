import os
import random
import requests
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, render_template_string

app = Flask(__name__)
app.secret_key = 'vilen_secret_key_security_999'

ADMIN_PASSWORD = 'vilen1234'
DATABASE = 'vilen_world.db'

# --- ডাটাবেজ ইনিশিয়ালাইজেশন ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ১. মেম্বার টেবিল (অটো পিন ও জেলা সহ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            pin TEXT NOT NULL,
            district TEXT NOT NULL,
            membership_tier TEXT NOT NULL,
            facebook_id TEXT,
            status TEXT DEFAULT 'Active',
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ২. ট্রেডিং সিগন্যাল টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_pair TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            entry_price TEXT NOT NULL,
            target_price TEXT NOT NULL,
            stop_loss TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ৩. একাধিক ফেসবুক পেজ টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fb_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT NOT NULL,
            page_id TEXT NOT NULL,
            page_token TEXT NOT NULL,
            auto_message TEXT,
            connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# --- রিয়েল মার্কেট লাইভ সিগন্যাল ফেচ করার ফাংশন (Binance API) ---
def fetch_real_market_signals():
    live_signals = []
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                symbol = item['symbol']
                if symbol in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']:
                    price = float(item['lastPrice'])
                    price_change = float(item['priceChangePercent'])
                    
                    sig_type = "BUY (CALL)" if price_change >= 0 else "SELL (PUT)"
                    entry = f"{price:.2f}"
                    target = f"{price * 1.015:.2f}" if "BUY" in sig_type else f"{price * 0.985:.2f}"
                    sl = f"{price * 0.992:.2f}" if "BUY" in sig_type else f"{price * 1.008:.2f}"
                    
                    pair_name = symbol.replace('USDT', '/USDT')
                    live_signals.append({
                        'asset_pair': pair_name,
                        'signal_type': sig_type,
                        'entry_price': entry,
                        'target_price': target,
                        'stop_loss': sl
                    })
    except Exception as e:
        pass
    
    if not live_signals:
        conn = get_db_connection()
        db_sigs = conn.execute('SELECT * FROM signals ORDER BY id DESC LIMIT 5').fetchall()
        conn.close()
        for s in db_sigs:
            live_signals.append({
                'asset_pair': s['asset_pair'],
                'signal_type': s['signal_type'],
                'entry_price': s['entry_price'],
                'target_price': s['target_price'],
                'stop_loss': s['stop_loss']
            })
            
    return live_signals

# --- ১. মূল ল্যান্ডিং পেজ (স্লোগান ও রিয়েল মার্কেট সিগন্যাল সহ) ---
@app.route('/')
def home():
    signals = fetch_real_market_signals()
    
    landing_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>VÎLËŇ WØRLD TÊAM GRØUP - 64 Districts United</title>
        <style>
            body { background: #0b0f19; color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; text-align: center; }
            .hero { padding: 50px 20px; background: radial-gradient(circle, rgba(212,175,55,0.15) 0%, rgba(11,15,25,1) 80%); border-bottom: 1px solid rgba(212,175,55,0.3); }
            h1 { color: #d4af37; text-transform: uppercase; font-size: 30px; letter-spacing: 2px; margin-bottom: 10px; }
            .slogan-box { background: rgba(255,255,255,0.03); border: 2px dashed #d4af37; padding: 25px; border-radius: 15px; max-width: 820px; margin: 20px auto; backdrop-filter: blur(10px); text-align: left; }
            .slogan-box h3 { color: #d4af37; font-size: 19px; margin-bottom: 12px; text-align: center; text-transform: uppercase; letter-spacing: 1px; }
            .slogan-box p { color: #e5e7eb; font-size: 15px; line-height: 1.7; margin-bottom: 10px; }
            .btn-group { margin-top: 25px; }
            .btn { background: linear-gradient(135deg, #d4af37, #aa771c); color: #000; padding: 12px 25px; border-radius: 25px; text-decoration: none; font-weight: bold; margin: 0 10px; display: inline-block; box-shadow: 0 0 15px rgba(212,175,55,0.4); }
            .btn-admin { background: rgba(255,255,255,0.1); color: #d4af37; border: 1px solid #d4af37; }
            .signals-section { max-width: 800px; margin: 40px auto; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; background: rgba(255,255,255,0.02); border-radius: 10px; overflow: hidden; }
            th, td { border: 1px solid rgba(255,255,255,0.1); padding: 10px; text-align: center; font-size: 14px; }
            th { background: rgba(212,175,55,0.2); color: #d4af37; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>VÎLËŇ WØRLD TÊAM GRØUP</h1>
            <p style="color: #9ca3af; letter-spacing: 1px;">Official Team Identity, Real Market Signals & Community Platform</p>
            
            <div class="slogan-box">
                <h3>⚡ আমাদের মূল স্লোগান ও ঐতিহাসিক অঙ্গীকার ⚡</h3>
                <p>🚩 <strong>এক্টিভ টিম পরিচিতি:</strong> ৬৪টা জেলা থেকে আমরা আলাদা কেউ নই—বরং ৬৪টা জেলা মিলিয়েই আমাদের একটাই অবিচ্ছেদ্য ও শক্তিশালী টিম!</p>
                <p>🚫 <strong>অপরাধ প্রতিরোধ:</strong> আমাদের বাংলাদেশ থেকে মাদক কারবারি, ধর্ষণকারী এবং ছিনতাইকারীদের চিরতরে প্রতিহত করব। ভিলেন ওয়ার্ল্ড টিমের কোনো সদস্য কখনো মাদক স্পর্শ করবে না এবং সবসময় মাদক থেকে দূরে থাকবে।</p>
                <p>⚖️ <strong>আইনের প্রতি শ্রদ্ধা:</strong> আমরা আইন নিজের হাতে তুলে নেব না; যেকোনো অন্যায় বা অপরাধের বিরুদ্ধে আমরা সবসময় দেশের প্রচলিত <strong>আইনের সাহায্য নেব</strong> এবং প্রশাসনকে পূর্ণ সহযোগিতা করব।</p>
            </div>

            <div class="btn-group">
                <a href="/user-login" class="btn">Member ID Portal Login</a>
                <a href="/admin" class="btn btn-admin">Master Admin Panel</a>
            </div>
        </div>

        <div class="signals-section">
            <h2 style="color: #d4af37; text-transform: uppercase;">Real-Time Live Market Signal Feeds</h2>
            <table>
                <tr><th>Asset Pair</th><th>Signal Type</th><th>Live Entry Price</th><th>Target (TP)</th><th>Stop Loss (SL)</th></tr>
                {% for s in signals %}
                <tr>
                    <td><b>{{ s.asset_pair }}</b></td>
                    <td style="color: {{ 'lime' if 'BUY' in s.signal_type else 'red' }}; font-weight: bold;">{{ s.signal_type }}</td>
                    <td>{{ s.entry_price }}</td>
                    <td>{{ s.target_price }}</td>
                    <td>{{ s.stop_loss }}</td>
                </tr>
                {% else %}
                <tr><td colspan="5" style="color: #9ca3af;">Connecting to real market feed...</td></tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(landing_html, signals=signals)

# --- ২. মেম্বার ইউজার লগইন রাউট ---
@app.route('/user-login', methods=['GET', 'POST'])
def user_login():
    error = None
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        pin = request.form.get('pin')
        
        conn = get_db_connection()
        member = conn.execute('SELECT * FROM members WHERE mobile = ? AND pin = ?', (mobile, pin)).fetchone()
        conn.close()
        
        if member:
            session['member_id'] = member['id']
            return redirect(url_for('my_id_card'))
        else:
            error = 'Invalid Mobile Number or PIN. Please try again.'
            
    login_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Member Login - VÎLËŇ WØRLD</title>
        <style>
            body { background: #0b0f19; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(212,175,55,0.3); padding: 30px; border-radius: 15px; width: 320px; text-align: center; backdrop-filter: blur(10px); }
            input, button { width: 100%; padding: 12px; margin: 10px 0; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; border-radius: 8px; box-sizing: border-box; }
            button { background: linear-gradient(135deg, #d4af37, #aa771c); color: #000; font-weight: bold; cursor: pointer; border: none; }
            h2 { color: #d4af37; text-transform: uppercase; font-size: 20px; }
            .error { color: #ff6b6b; font-size: 13px; margin-bottom: 10px; }
            .home-link { display: inline-block; margin-top: 15px; color: #d4af37; text-decoration: none; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Member ID Portal</h2>
            <p style="font-size: 12px; color: #9ca3af;">Login with Mobile & Auto-PIN</p>
            {% if error %}<p class="error">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="text" name="mobile" placeholder="Mobile Number" required>
                <input type="password" name="pin" placeholder="Auto-Generated PIN" required>
                <button type="submit">View My ID Card</button>
            </form>
            <a href="/" class="home-link">← Back to Home</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_html, error=error)

# --- ৩. মেম্বার আইডি কার্ড ও ডাউনলোড পেজ ---
@app.route('/my-id')
def my_id_card():
    member_id = session.get('member_id')
    if not member_id:
        return redirect(url_for('user_login'))
        
    conn = get_db_connection()
    member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    conn.close()

    if not member:
        return redirect(url_for('user_login'))

    id_card_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ID Card - {{ member.name }}</title>
        <style>
            body { background: #0b0f19; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; font-family: 'Segoe UI', sans-serif; margin: 0; }
            .id-card { width: 340px; height: 500px; background: linear-gradient(145deg, #111827, #0b0f19); border: 2px solid #d4af37; border-radius: 15px; box-shadow: 0 0 25px rgba(212, 175, 55, 0.4); padding: 20px; text-align: center; color: white; position: relative; }
            .avatar { width: 90px; height: 90px; border-radius: 50%; border: 3px solid #d4af37; margin: 15px auto 10px; background: #1f2937; display: flex; justify-content: center; align-items: center; font-size: 32px; color: #d4af37; font-weight: bold; }
            h2 { color: #d4af37; margin: 5px 0 0 0; text-transform: uppercase; font-size: 18px; letter-spacing: 1px; }
            .tier { background: #d4af37; color: #000; font-weight: bold; display: inline-block; padding: 4px 15px; border-radius: 12px; margin-top: 8px; font-size: 12px; text-transform: uppercase; }
            .details { margin-top: 15px; text-align: left; font-size: 13px; background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
            .details div { margin-bottom: 6px; display: flex; justify-content: space-between; }
            .footer { position: absolute; bottom: 12px; left: 0; right: 0; font-size: 10px; color: #6b7280; letter-spacing: 1px; }
            .btn-box { margin-top: 15px; display: flex; gap: 10px; justify-content: center; }
            .action-btn { background: #38bdf8; color: #000; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 12px; cursor: pointer; border: none; }
            .logout-btn { background: #ff6b6b; color: #fff; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="id-card">
            <h3 style="color:#d4af37; margin:0; letter-spacing:2px; font-size: 13px;">VÎLËŇ WØRLD TÊAM</h3>
            <div class="avatar">{{ member.name[0] }}</div>
            <h2>{{ member.name }}</h2>
            <div class="tier">{{ member.membership_tier }}</div>

            <div class="details">
                <div><span>Member ID:</span> <strong>#VWT-00{{ member.id }}</strong></div>
                <div><span>District:</span> <strong style="color: #d4af37;">{{ member.district }}</strong></div>
                <div><span>Mobile:</span> <strong>{{ member.mobile }}</strong></div>
                <div><span>Auto PIN:</span> <strong style="color: #38bdf8;">{{ member.pin }}</strong></div>
                <div><span>Status:</span> <strong style="color: lime;">{{ member.status }}</strong></div>
            </div>

            <div class="footer">64 DISTRICTS UNITED TEAM</div>
        </div>

        <div class="btn-box">
            <button class="action-btn" onclick="window.print()">Download / Print ID Card</button>
            <a href="/user-logout" class="logout-btn">Logout</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(id_card_html, member=member)

@app.route('/user-logout')
def user_logout():
    session.pop('member_id', None)
    return redirect(url_for('user_login'))

# --- ৪. ফেসবুক পেজ অটোমেশন (অ্যাডমিন) ---
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
        
        if p_name
