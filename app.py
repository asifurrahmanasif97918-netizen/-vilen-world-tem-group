from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'vilen_secret_key_vwt_ultimate_final'

# ডাটাবেজ সেটআপ
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
            phone TEXT,
            district TEXT,
            tier TEXT,
            secret_pin TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ১. হোম পেজ (নিয়ন লাইটিং, শপথ বক্স ও আলাদা লগইন অপশন)
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VÎLËŇ WØRLD TÊAM GRØUP - Command Hub</title>
    <style>
        body { background-color: #0b0f19; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; text-align: center; }
        .header { padding: 25px; border-bottom: 2px solid #d4af37; box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); }
        .logo { font-size: 28px; font-weight: bold; color: #d4af37; text-shadow: 0 0 10px #d4af37, 0 0 20px #00f0ff; }
        .container { max-width: 500px; margin: 20px auto; padding: 20px; background: #111827; border: 2px solid #d4af37; border-radius: 12px; box-shadow: 0 0 25px rgba(212, 175, 55, 0.2); }
        .pledge-box { background: #0b0f19; border: 2px dashed #00f0ff; padding: 15px; margin: 15px 0; border-radius: 8px; text-align: left; font-size: 13px; color: #cbd5e1; box-shadow: 0 0 10px rgba(0,240,255,0.2); }
        .pledge-box h4 { color: #d4af37; text-align: center; margin-top: 0; }
        .btn { display: block; width: 100%; padding: 12px; margin: 10px 0; background: linear-gradient(135deg, #d4af37, #b45309); color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 16px; box-shadow: 0 0 10px rgba(212,175,55,0.4); }
        .btn-admin { background: linear-gradient(135deg, #ef4444, #991b1b); color: #fff; box-shadow: 0 0 10px rgba(239,68,68,0.4); }
        input { width: 90%; padding: 10px; margin: 8px 0; background: #1f293d; border: 1px solid #d4af37; color: #fff; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">👑 VÎLËŇ WØRLD TÊAM GRØUP</div>
        <p style="color: #00f0ff; font-size: 13px; text-shadow: 0 0 5px #00f0ff;">৬৪ জেলার যৌথ শক্তিশালী টিম ও কমান্ড হাব</p>
    </div>

    <div class="container">
        <!-- অপরাধ বিরোধী অঙ্গীকার বক্স -->
        <div class="pledge-box">
            <h4>🛡️ আমাদের অঙ্গীকার ও শপথ</h4>
            <p><b>৬৪ জেলার ঐক্য:</b> ৬৪টা জেলা থেকে আমরা আলাদা কেউ নই—বরং ৬৪টা জেলা মিলিয়েই আমাদের একটাই অবিচ্ছেদ্য ও শক্তিশালী টিম!</p>
            <p><b>অপরাধ প্রতিরোধ:</b> বাংলাদেশ থেকে মাদক কারবারি, ধর্ষণকারী এবং ছিনতাইকারীদের চিরতরে প্রতিহত করা। ভিলেন ওয়ার্ল্ড টিমের কোনো সদস্য কখনো মাদক স্পর্শ করবে না।</p>
            <p><b>আইনের প্রতি শ্রদ্ধা:</b> আইন নিজের হাতে না তুলে নিয়ে দেশের প্রচলিত আইনের সাহায্য নেওয়া এবং প্রশাসনকে সহযোগিতা করা।</p>
        </div>

        <h3>🔐 মাস্টার অ্যাডমিন ভল্ট</h3>
        <form method="POST" action="/admin-login">
            <input type="password" name="password" placeholder="মাস্টার পাসওয়ার্ড দিন..." required>
            <button type="submit" class="btn btn-admin">অ্যাডমিন ড্যাশবোর্ডে প্রবেশ</button>
        </form>

        <hr style="border-color: #374151; margin: 20px 0;">
        
        <h3>🆔 মেম্বার পোর্টাল (ইউজার লগইন)</h3>
        <form method="POST" action="/user-login">
            <input type="text" name="phone" placeholder="মোবাইল নম্বর (যেমন: 0130...)" required>
            <input type="password" name="secret_pin" placeholder="৪ সংখ্যার সিক্রেট পিন" required>
            <button type="submit" class="btn">মেম্বার ড্যাশবোর্ডে প্রবেশ</button>
        </form>
    </div>
</body>
</html>
'''

# ২. আলাদা অ্যাডমিন ড্যাশবোর্ড (মেম্বার ও ফেসবুক বট কন্ট্রোল)
ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VWT - Master Admin Dashboard</title>
    <style>
        body { background-color: #0b0f19; color: #fff; font-family: sans-serif; margin: 0; padding: 15px; }
        .container { max-width: 550px; margin: 20px auto; background: #111827; border: 2px solid #ef4444; border-radius: 12px; padding: 20px; box-shadow: 0 0 20px rgba(239,68,68,0.3); }
        h2 { color: #ef4444; text-align: center; font-size: 20px; text-shadow: 0 0 8px #ef4444; }
        h3 { color: #00f0ff; border-bottom: 1px solid #374151; padding-bottom: 5px; margin-top: 25px; }
        label { font-size: 13px; color: #cbd5e1; display: block; margin-top: 10px; }
        input, textarea, select { width: 100%; padding: 10px; margin-top: 5px; background: #1f293d; border: 1px solid #4b5563; color: #fff; border-radius: 5px; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; margin-top: 15px; background: linear-gradient(135deg, #d4af37, #b45309); color: #000; font-weight: bold; border: none; border-radius: 5px; cursor: pointer; }
        .back-btn { display: inline-block; margin-top: 15px; padding: 8px 15px; background: #1f293d; color: #38bdf8; text-decoration: none; border-radius: 5px; font-size: 13px; border: 1px solid #38bdf8; }
    </style>
</head>
<body>
    <div class="container">
        <h2>👑 মাস্টার অ্যাডমিন ড্যাশবোর্ড</h2>

        <h3>👤 নতুন মেম্বার ও লিডার রেজিস্ট্রেশন</h3>
        <form method="POST" action="/add-member">
            <label>মেম্বারের পূর্ণ নাম:</label>
            <input type="text" name="full_name" placeholder="পূর্ণ নাম লিখুন..." required>
            
            <label>মোবাইল নম্বর:</label>
            <input type="text" name="phone" placeholder="0130xxxxxxxx" required>
            
            <label>জেলার নাম:</label>
            <input type="text" name="district" placeholder="যেমন: ময়মনসিংহ / ঢাকা" required>
            
            <label>টায়ার / পদবী:</label>
            <select name="tier">
                <option value="Master Lead">Master Lead (মাস্টার লিডার)</option>
                <option value="VIP Member">VIP Member (ভিআইপি মেম্বার)</option>
                <option value="Pro Trader">Pro Trader (প্রো ট্রেডার)</option>
            </select>
            
            <button type="submit" class="btn">মেম্বার সেভ করুন ও অটো-পিন জেনারেট করুন</button>
        </form>

        <h3>🤖 ফেসবুক পেজ ও কমেন্ট-ইনবক্স অটোমেশন বট</h3>
        <form method="POST" action="/add-page">
            <label>ফেসবুক পেজ নাম:</label>
            <input type="text" name="page_name" placeholder="যেমন: VÎLËŇ WØRLD TÊAM" required>
            
            <label>ফেসবুক পেজ আইডি:</label>
            <input type="text" name="page_id" placeholder="পেজ আইডি দিন..." required>
            
            <label>পার্মানেন্ট এক্সেস টোকেন:</label>
            <input type="text" name="access_token" placeholder="EAAB... টোকেন পেস্ট করুন" required>
            
            <label>ইনবক্স অফার লিংক / অটো কমেন্ট মেসেজ:</label>
            <textarea name="auto_reply" rows="3" required>হ্যালো! ভিলেন ওয়ার্ল্ড টিমে যুক্ত হওয়ার জন্য ধন্যবাদ।</textarea>
            
            <button type="submit" class="btn" style="background: linear-gradient(135deg, #ef4444, #991b1b); color: #fff;">ফেসবুক বট চালু করুন</button>
        </form>

        <div style="text-align: center;">
            <a href="/" class="back-btn">← লগআউট করে হোম পেজে যান</a>
        </div>
    </div>
</body>
</html>
'''

# ৩. আলাদা মেম্বার ড্যাশবোর্ড ও ডিজিটাল আইডি কার্ড
MEMBER_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VWT - Member Dashboard & ID Card</title>
    <style>
        body { background-color: #0b0f19; color: #fff; font-family: sans-serif; margin: 0; padding: 15px; text-align: center; }
        .card { max-width: 400px; margin: 30px auto; background: linear-gradient(135deg, #111827, #1f293d); border: 2px solid #d4af37; border-radius: 15px; padding: 25px; box-shadow: 0 0 30px rgba(212,175,55,0.4); }
        .card h2 { color: #d4af37; margin-bottom: 5px; text-shadow: 0 0 10px #d4af37; }
        .badge { background: #00f0ff; color: #000; padding: 4px 12px; border-radius: 15px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 15px; }
        .info { text-align: left; background: #0b0f19; padding: 15px; border-radius: 8px; border: 1px solid #374151; font-size: 14px; line-height: 1.6; }
        .info span { color: #00f0ff; font-weight: bold; }
        .back-btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1f293d; color: #d4af37; text-decoration: none; border-radius: 6px; border: 1px solid #d4af37; }
    </style>
</head>
<body>
    <div class="card">
        <h2>👑 VÎLËŇ WØRLD TÊAM</h2>
        <div class="badge">মেম্বার ড্যাশবোর্ড - ভেরিফাইড আইডি কার্ড</div>
        
        <div class="info">
            <p><b>মেম্বার আইডি:</b> <span>#VWT-2026-{{ member[0] }}</span></p>
            <p><b>পূর্ণ নাম:</b> <span>{{ member[1] }}</span></p>
            <p><b>মোবাইল নম্বর:</b> <span>{{ member[2] }}</span></p>
            <p><b>জেলা:</b> <span>{{ member[3] }}</span></p>
            <p><b>পদবী / টায়ার:</b> <span>{{ member[4] }}</span></p>
            <p><b>সিক্রেট পিন:</b> <span style="color:#ef4444;">{{ member[5] }}</span></p>
        </div>

        <a href="/" class="back-btn">← হোম পেজে ফিরে যান</a>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/admin-login', methods=['POST'])
def admin_login():
    password = request.form.get('password')
    if password == 'vilen1234':  # মাস্টার পাসওয়ার্ড
        session['admin_logged'] = True
        return redirect(url_for('admin_dashboard'))
    return "<script>alert('ভুল মাস্টার পাসওয়ার্ড!'); window.location.href='/';</script>"

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('home'))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE)

@app.route('/add-member', methods=['POST'])
def add_member():
    if not session.get('admin_logged'):
        return redirect(url_for('home'))
    
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    district = request.form.get('district')
    tier = request.form.get('tier')
    secret_pin = str(random.randint(1000, 9999))  # ৪ সংখ্যার অটো-পিন জেনারেটর
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (full_name, phone, district, tier, secret_pin) VALUES (?, ?, ?, ?, ?)",
                   (full_name, phone, district, tier, secret_pin))
    conn.commit()
    conn.close()
    
    return f"<script>alert('সফলভাবে মেম্বার সেভ হয়েছে! অটো-জেনারেটেড সিক্রেট পিন হলো: {secret_pin}'); window.location.href='/admin-dashboard';</script>"

@app.route('/user-login', methods=['POST'])
def user_login():
    phone = request.form.get('phone')
    secret_pin = request.form.get('secret_pin')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE phone = ? AND secret_pin = ?", (phone, secret_pin))
    member = cursor.fetchone()
    conn.close()
    
    if member:
        return render_template_string(MEMBER_DASHBOARD_TEMPLATE, member=member)
    return "<script>alert('মোবাইল নম্বর অথবা সিক্রেট পিন ভুল হয়েছে!'); window.location.href='/';</script>"

@app.route('/add-page', methods=['POST'])
def add_page():
    if not session.get('admin_logged'):
        return redirect(url_for('home'))
    
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
    
    return "<script>alert('ফেসবুক পেজ ও কমেন্ট-ইনবক্স বট সফলভাবে কানেক্ট হয়েছে!'); window.location.href='/admin-dashboard';</script>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
