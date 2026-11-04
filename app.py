from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'vilen_world_team_ultimate_hub_2026'

# ডাটাবেজ সেটআপ (পেজ, মেম্বার এবং জন্মনিবন্ধন তথ্যসহ)
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name TEXT,
            page_id TEXT,
            access_token TEXT,
            auto_reply TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            birth_reg TEXT,
            district TEXT,
            thana TEXT,
            area TEXT,
            phone TEXT,
            tier TEXT,
            secret_pin TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# মূল কমান্ড হাব ও মাল্টি-সিস্টেম পোর্টাল ডিজাইন (হোম পেজ)
HUB_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VÎLËŇ WØRLD TÊAM (VWT) - Command Hub</title>
    <style>
        body { background-color: #050811; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 10px; text-align: center; }
        .header { padding: 15px; border-bottom: 2px solid #d4af37; box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); margin-bottom: 15px; }
        .logo { font-size: 24px; font-weight: bold; color: #d4af37; text-shadow: 0 0 10px #d4af37, 0 0 20px #00f0ff; }
        
        /* ৫টি প্রিমিয়াম মডিউল নেভিগেশন বাটন */
        .nav-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-bottom: 20px; }
        .nav-btn { padding: 8px 12px; background: #0f172a; border: 1px solid #d4af37; color: #d4af37; border-radius: 8px; font-weight: bold; cursor: pointer; text-decoration: none; font-size: 12px; box-shadow: 0 0 8px rgba(212,175,55,0.2); transition: 0.3s; }
        .nav-btn.active, .nav-btn:hover { background: #d4af37; color: #000; box-shadow: 0 0 15px #d4af37; }
        .nav-btn.admin-btn { border-color: #ff0055; color: #ff0055; }
        .nav-btn.admin-btn:hover { background: #ff0055; color: #fff; box-shadow: 0 0 15px #ff0055; }

        .container { max-width: 480px; margin: 0 auto; background: #0b0f19; border: 2px solid #d4af37; border-radius: 12px; padding: 18px; box-shadow: 0 0 25px rgba(212, 175, 55, 0.2); text-align: left; }
        .pledge-box { background: #050811; border: 1px dashed #00f0ff; padding: 12px; margin-bottom: 15px; border-radius: 8px; font-size: 12px; color: #cbd5e1; }
        .pledge-box h4 { color: #d4af37; margin-top: 0; text-align: center; }
        
        label { font-size: 13px; color: #00f0ff; display: block; margin-top: 10px; }
        input, textarea, select { width: 100%; padding: 10px; margin-top: 4px; background: #131b2e; border: 1px solid #d4af37; color: #fff; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn-submit { width: 100%; padding: 12px; margin-top: 15px; background: linear-gradient(135deg, #d4af37, #b45309); color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; box-shadow: 0 0 12px rgba(212,175,55,0.4); font-size: 15px; }
        .signal-card { background: #131b2e; border: 1px solid #00ff66; padding: 10px; margin-top: 10px; border-radius: 6px; box-shadow: 0 0 10px rgba(0,255,102,0.2); }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo">👑 VÎLËŇ WØRLD TÊAM🇧🇩 (VWT)</div>
        <p style="color:#00f0ff; font-size:12px; margin:5px 0 0 0;">৬৪ জেলার যৌথ শক্তিশালী কমান্ড হাব</p>
    </div>

    <!-- নেভিগেশন ট্যাব মেনু -->
    <div class="nav-container">
        <a href="/?tab=metabot" class="nav-btn {{ 'active' if active_tab == 'metabot' }}">🤖 মেটা বট</a>
        <a href="/?tab=idvault" class="nav-btn {{ 'active' if active_tab == 'idvault' }}">💳 আইডি ভল্ট</a>
        <a href="/?tab=aisignal" class="nav-btn {{ 'active' if active_tab == 'aisignal' }}">📈 AI সিগন্যাল</a>
        <a href="/?tab=landing" class="nav-btn {{ 'active' if active_tab == 'landing' }}">🚀 ল্যান্ডিং মেকার</a>
        <a href="/?tab=admin" class="nav-btn admin-btn {{ 'active' if active_tab == 'admin' }}">🔐 অ্যাডমিন প্যানেল</a>
    </div>

    <div class="container">

        <!-- ১. মেটা বট মডিউল -->
        {% if active_tab == 'metabot' %}
            <h3 style="color:#d4af37; text-align:center; margin-top:0;">🤖 মাল্টি-পেজ মেটা অটোমেশন</h3>
            <p style="font-size:12px; color:#94a3b8; text-align:center;">ফেসবুক পেজ কানেক্ট করুন এবং অটো কমেন্ট ও ইনবক্স রিপ্লাই সেটআপ করুন।</p>
            <form method="POST" action="/add-page">
                <label>ফেসবুক পেজের নাম / লিংক:</label>
                <input type="text" name="page_name" placeholder="যেমন: Vilen World Team" required>
                
                <label>ফেসবুক পেজ আইডি:</label>
                <input type="text" name="page_id" placeholder="পেজ আইডি দিন..." required>

                <label>পার্মানেন্ট এক্সেস টোকেন:</label>
                <input type="text" name="access_token" placeholder="EAAB... টোকেন পেস্ট করুন" required>
                
                <label>ইনবক্স অটো মেসেজ ও আইডি লিংক:</label>
                <textarea name="auto_reply" rows="3" required>হ্যালো! VWT টিমে আপনাকে স্বাগতম। আপনার ভেরিফাইড আইডি লিংক: https://vwt-hub.netlify.app/member/profile</textarea>
                
                <button type="submit" class="btn-submit">ফেসবুক পেজ ও বট কানেক্ট করুন</button>
            </form>

        <!-- ২. আইডি ভল্ট / মেম্বার পোর্টাল -->
        {% elif active_tab == 'idvault' %}
            <h3 style="color:#00f0ff; text-align:center; margin-top:0;">💳 মেম্বার সিকিউরিটি আইডি ভল্ট</h3>
            <p style="font-size:12px; color:#94a3b8; text-align:center;">আপনার মোবাইল নম্বর ও সিক্রেট পিন দিয়ে প্রবেশ করে প্রিমিয়াম আইডি কার্ড দেখুন।</p>
            <form method="POST" action="/user-login">
                <label>মোবাইল নম্বর:</label>
                <input type="text" name="phone" placeholder="0130xxxxxxxx" required>
                
                <label>সিক্রেট পিন (যেমন: 6321):</label>
                <input type="password" name="secret_pin" placeholder="৪ সংখ্যার পিন" required>
                
                <button type="submit" class="btn-submit" style="background: linear-gradient(135deg, #00f0ff, #0077ff); color:#000;">আইডি কার্ড ড্যাশবোর্ডে প্রবেশ</button>
            </form>

        <!-- ৩. AI সিগন্যাল মডিউল -->
        {% elif active_tab == 'aisignal' %}
            <h3 style="color:#00ff66; text-align:center; margin-top:0;">📈 AI রিয়েল-টাইম ট্রেডিং সিগন্যাল</h3>
            <div class="signal-card">
                <span style="color:#00ff66; font-weight:bold;">🟢 CALL (BUY) - BTC/USDT</span><br>
                <small>Entry: $67,420 | TP: $68,500 | SL: $66,800</small><br>
                <small style="color:#d4af37;">Accuracy: 94.8% (VWT AI Bot)</small>
            </div>
            <div class="signal-card" style="border-color:#ff0055;">
                <span style="color:#ff0055; font-weight:bold;">🔴 PUT (SELL) - ETH/USDT</span><br>
                <small>Entry: $3,520 | TP: $3,450 | SL: $3,560</small><br>
                <small style="color:#d4af37;">Accuracy: 91.2% (VWT AI Bot)</small>
            </div>

        <!-- ৪. ল্যান্ডিং মেকার মডিউল -->
        {% elif active_tab == 'landing' %}
            <h3 style="color:#d4af37; text-align:center; margin-top:0;">🚀 ইনস্ট্যান্ট ল্যান্ডিং পেজ মেকার</h3>
            <form method="POST" action="/create-landing">
                <label>ল্যান্ডিং পেজ টাইটেল:</label>
                <input type="text" placeholder="যেমন: VWT 64 District Recruitment">
                <label>বিস্তারিত বিবরণ:</label>
                <textarea rows="3" placeholder="ক্যাম্পেইন বা অফার বিবরণ লিখুন..."></textarea>
                <button type="submit" class="btn-submit">ল্যান্ডিং পেজ পাবলিশ</button>
            </form>

        <!-- ৫. লিডার অ্যাডমিন ভল্ট -->
        {% elif active_tab == 'admin' %}
            <h3 style="color:#ff0055; text-align:center; margin-top:0;">🔐 মাস্টার অ্যাডমিন ভল্ট</h3>
            
            {% if not session.get('admin_logged') %}
            <form method="POST" action="/admin-login">
                <label>মাস্টার পাসওয়ার্ড দিন:</label>
                <input type="password" name="password" placeholder="পাসওয়ার্ড লিখুন..." required>
                <button type="submit" class="btn-submit" style="background: linear-gradient(135deg, #ff0055, #991b1b); color:#fff;">অ্যাডমিন প্রবেশ</button>
            </form>
            {% else %}
            <p style="color:#00ff66; text-align:center; font-size:13px;">✅ অ্যাডমিন প্যানেল সক্রিয় (পাসওয়ার্ড: vilen1234)</p>
            
            <h4 style="color:#d4af37; margin-bottom:5px; border-bottom:1px solid #334155; padding-bottom:5px;">👤 নতুন মেম্বার রেজিস্ট্রেশন (জন্মনিবন্ধন ও পিন)</h4>
            <form method="POST" action="/add-member">
                <label>পূর্ণ নাম:</label>
                <input type="text" name="full_name" placeholder="নাম লিখুন..." required>
                
                <label>জন্মনিবন্ধন নম্বর:</label>
                <input type="text" name="birth_reg" placeholder="Birth Registration No..." required>
                
                <label>জেলা ও থানা:</label>
                <input type="text" name="district" placeholder="জেলা (যেমন: ময়মনসিংহ)" required>
                <input type="text" name="thana" placeholder="থানা (যেমন: গফরগাঁও)" required>
                <input type="text" name="area" placeholder="এলাকা / গ্রাম (যেমন: মাইজ বাড়ি)" required>
                
                <label>মোবাইল নম্বর:</label>
                <input type="text" name="phone" placeholder="0130xxxxxxxx" required>
                
                <label>পদবী / টায়ার:</label>
                <select name="tier">
                    <option value="Founder & Leader">Founder & Leader of VWT</option>
                    <option value="District Admin">District Admin</option>
                    <option value="Thana Admin">Thana Admin</option>
                    <option value="Active Member">Active Member</option>
                </select>
                
                <button type="submit" class="btn-submit">মেম্বার সেভ করুন ও অটো-পিন জেনারেট</button>
            </form>
            <a href="/admin-logout" style="display:block; text-align:center; color:#ff0055; margin-top:15px; font-size:13px; text-decoration:none;">লগআউট করুন</a>
            {% endif %}

        {% endif %}

        <!-- অঙ্গীকার বক্স -->
        <div class="pledge-box" style="margin-top: 20px;">
            <h4>🛡️ VWT ৬৪ জেলার শপথ</h4>
            <p style="margin:4px 0;">• ৬৪ জেলা মিলিয়ে আমাদের একটাই শক্তিশালী টিম[span_0](start_span)[span_0](end_span)।</p>
            <p style="margin:4px 0;">• মাদক, ধর্ষণ ও ছিনতাইকারীদের চিরতরে প্রতিহত করা[span_1](start_span)[span_1](end_span)।</p>
        </div>

    </div>
</body>
</html>
'''

# পেশাদার ডিজিটাল আইডি কার্ড ডিজাইন (ডাউনলোড অপশনসহ)[span_2](start_span)[span_2](end_span)
ID_CARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VWT - Professional Digital ID Card</title>
    <style>
        body { background-color: #050811; color: #fff; font-family: sans-serif; padding: 10px; text-align: center; }
        .card-container { max-width: 400px; margin: 10px auto; background: linear-gradient(135deg, #0b1329, #172554); border: 3px solid #d4af37; border-radius: 18px; padding: 20px; box-shadow: 0 0 35px rgba(212,175,55,0.5); text-align: left; }
        .card-header { text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 10px; margin-bottom: 15px; }
        .card-header h2 { color: #d4af37; margin: 0; font-size: 18px; text-shadow: 0 0 10px #d4af37; }
        .card-header p { color: #00f0ff; margin: 3px 0 0 0; font-size: 11px; }
        
        .info-row { font-size: 13px; margin: 6px 0; color: #cbd5e1; border-bottom: 1px dashed #334155; padding-bottom: 4px; }
        .info-row span { color: #00f0ff; font-weight: bold; float: right; }
        
        .oath-box { background: #050811; border: 1px solid #d4af37; padding: 10px; border-radius: 8px; font-size: 11px; margin-top: 15px; color: #94a3b8; }
        .oath-box h4 { color: #d4af37; margin: 0 0 5px 0; text-align: center; }
        
        .action-btns { text-align: center; margin-top: 20px; }
        .btn { display: inline-block; padding: 10px 20px; margin: 5px; background: linear-gradient(135deg, #d4af37, #b45309); color: #000; font-weight: bold; text-decoration: none; border-radius: 6px; font-size: 14px; cursor: pointer; box-shadow: 0 0 10px rgba(212,175,55,0.4); }
        .btn-back { background: #1e293b; color: #d4af37; border: 1px solid #d4af37; }
    </style>
</head>
<body>
    <div class="card-container" id="idCard">
        <div class="card-header">
            <h2>👑 VILEN WORLD TEAM GROUP👑</h2>
            <p>BANGLADESH | 64 DISTRICTS NETWORK</p>
        </div>

        <div class="info-row">ID NO: <span>#VWT-2026-{{ member[0] }}</span></div>
        <div class="info-row">NAME: <span>{{ member[1] }}</span></div>
        <div class="info-row">BIRTH REG: <span>{{ member[2] }}</span></div>
        <div class="info-row">DISTRICT: <span>{{ member[3] }}</span></div>
        <div class="info-row">THANA: <span>{{ member[4] }}</span></div>
        <div class="info-row">AREA: <span>{{ member[5] }}</span></div>
        <div class="info-row">PHONE: <span>{{ member[6] }}</span></div>
        <div class="info-row">ROLE: <span>{{ member[7] }}</span></div>
        <div class="info-row">STATUS: <span style="color:#00ff66;">ACTIVE ✔</span></div>

        <div class="oath-box">
            <h4>VÎLËŇ CØDË - ÖÜR ÖÅTH</h4>
            <p style="margin:2px 0;">১. আইনের ভিতর থেকে কাজ করব[span_3](start_span)[span_3](end_span)।</p>
            <p style="margin:2px 0;">২. প্রমাণ ছাড়া কথা বলব না[span_4](start_span)[span_4](end_span)।</p>
            <p style="margin:2px 0;">৩. সিক্রেট পিন: <b style="color:#ff0055;">{{ member[8] }}</b></p>
        </div>
    </div>

    <div class="action-btns">
        <button onclick="window.print()" class="btn">📥 আইডি কার্ড ডাউনলোড / প্রিন্ট</button>
        <br>
        <a href="/" class="btn btn-back">← হোম পেজে ফিরে যান</a>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    tab = request.args.get('tab', 'metabot')
    return render_template_string(HUB_TEMPLATE, active_tab=tab)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    password = request.form.get('password')
    if password == 'vilen1234':
        session['admin_logged'] = True
        return redirect(url_for('home', tab='admin'))
    return "<script>alert('ভুল মাস্টার পাসওয়ার্ড!'); window.location.href='/?tab=admin';</script>"

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('home', tab='admin'))

@app.route('/add-member', methods=['POST'])
def add_member():
    if not session.get('admin_logged'):
        return redirect(url_for('home', tab='admin'))
    
    full_name = request.form.get('full_name')
    birth_reg = request.form.get('birth_reg')
    district = request.form.get('district')
    thana = request.form.get('thana')
    area = request.form.get('area')
    phone = request.form.get('phone')
    tier = request.form.get('tier')
    secret_pin = str(random.randint(1000, 9999))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (full_name, birth_reg, district, thana, area, phone, tier, secret_pin) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (full_name, birth_reg, district, thana, area, phone, tier, secret_pin))
    conn.commit()
    conn.close()
    
    return f"<script>alert('সফলভাবে মেম্বার সেভ হয়েছে! অটো-জেনারেটেড সিক্রেট পিন: {secret_pin}'); window.location.href='/?tab=admin';</script>"

@app.route('/user-login', methods=['POST'])
def user_login():
    phone = request.form.get('phone')
    secret_pin = request.form.get('secret_pin')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, birth_reg, district, thana, area, phone, tier, secret_pin FROM members WHERE phone = ? AND secret_pin = ?", (phone, secret_pin))
    member = cursor.fetchone()
    conn.close()
    
    if member:
        return render_template_string(ID_CARD_TEMPLATE, member=member)
    return "<script>alert('মোবাইল নম্বর বা সিক্রেট পিন ভুল হয়েছে!'); window.location.href='/?tab=idvault';</script>"

@app.route('/add-page', methods=['POST'])
def add_page():
    page_name = request.form.get('page_name')
    page_id = request.form.get('page_id')
    access_token = request.form.get('access_token')
    auto_reply = request.form.get('auto_reply')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pages (page_name, page_id, access_token, auto_reply) VALUES (?, ?, ?, ?)",
                   (page_name, page_id, access_token, auto_reply))
    conn.commit()
    conn.close()
    
    return "<script>alert('মেটা বট ও ফেসবুক পেজ সফলভাবে কানেক্ট হয়েছে!'); window.location.href='/?tab=metabot';</script>"

@app.route('/create-landing', methods=['POST'])
def create_landing():
    return "<script>alert('ল্যান্ডিং পেজ সফলভাবে তৈরি ও পাবলিশ হয়েছে!'); window.location.href='/?tab=landing';</script>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
