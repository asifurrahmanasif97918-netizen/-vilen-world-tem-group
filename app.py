
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'vilen_secret_key_security_999'

# Master Admin Password
ADMIN_PASSWORD = 'vilen1234'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid Master Password. Try again.'
    return render_template('admin_login.html', error=error)

@app.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Dashboard - VÎLËŇ WØRLD TÊAM GRØUP</title>
        <style>
            body { background-color: #0b0f19; color: #fff; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 50px; }
            .container { background: rgba(255,255,255,0.05); border: 1px solid rgba(212,175,55,0.3); border-radius: 15px; padding: 40px; max-width: 600px; margin: auto; backdrop-filter: blur(10px); }
            h1 { color: #d4af37; text-transform: uppercase; }
            .btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #ff6b6b; color: #fff; text-decoration: none; border-radius: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Admin Dashboard</h1>
            <p>VÎLËŇ WØRLD TÊAM GRØUP Master Control Panel Active.</p>
            <a href="/logout" class="btn">Logout</a>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host
