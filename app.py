import os
import sqlite3
from flask import Flask, request, redirect, url_for, session, render_template_string
from jinja2 import DictLoader, ChoiceLoader

app = Flask(__name__)
app.secret_key = "after13friday_cosmic_secret_key"
DATABASE = "database.db"

# ĐỊNH NGHĨA BỘ THEME MÀU SẮC (CÓ CẢ HOA MẪU ĐƠN)
THEMES = {
    "light-green": {
        "bg": "#f4f7f6",
        "card_bg": "#ffffff",
        "text": "#2d3748",
        "text_muted": "#718096",
        "primary": "#4a7c59",
        "accent": "#e8f5e9",
        "border": "#e2e8f0",
        "bg_img": "none",
        "star_opacity": "0"
    },
    "peony-pink": {
        "bg": "#fff5f7",
        "card_bg": "rgba(255, 255, 255, 0.92)",
        "text": "#4a1525",
        "text_muted": "#9c6475",
        "primary": "#d53f8c",
        "accent": "#ffe6ec",
        "border": "#fbb6ce",
        "bg_img": "url('https://images.unsplash.com/photo-1561181286-d3fee7d55364?q=80&w=1920&auto=format&fit=crop')",
        "star_opacity": "0"
    },
    "red-purple": {
        "bg": "#faf5ff",
        "card_bg": "#ffffff",
        "text": "#1a202c",
        "text_muted": "#718096",
        "primary": "#6b46c1",
        "accent": "#fff5f5",
        "border": "#e9d8fd",
        "bg_img": "none",
        "star_opacity": "0"
    },
    "cosmic-dark": {
        "bg": "linear-gradient(135deg, #06060c, #110e26, #1b163a)",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "text": "#c5c6c7",
        "text_muted": "#888888",
        "primary": "#66fcf1",
        "accent": "rgba(69,243,255,0.1)",
        "border": "rgba(255,255,255,0.08)",
        "bg_img": "none",
        "star_opacity": "0.5"
    }
}

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            stars INTEGER DEFAULT 50,
            is_blocked INTEGER DEFAULT 0
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            chapters INTEGER DEFAULT 1,
            views INTEGER DEFAULT 0,
            author_name TEXT NOT NULL,
            star_cost INTEGER DEFAULT 5
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        
        try:
            conn.execute("INSERT INTO users (username, password, role, stars) VALUES ('admin', 'admin123', 'admin', 999999)")
        except sqlite3.IntegrityError:
            pass
            
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('current_theme', 'peony-pink')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('announcement', 'Nơi những câu chuyện chạm đến tận cùng cảm xúc')")
        conn.commit()

init_db()

@app.before_request
def check_user_status():
    if 'user_id' in session:
        db = get_db()
        user = db.execute("SELECT is_blocked FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if user and user['is_blocked'] == 1:
            session.clear()
            return f"""
            <div style="background:#0f0c1b; color:#ff4d4d; text-align:center; padding:50px; font-family:sans-serif;">
                <h2>🚫 TÀI KHOẢN CỦA BẠN ĐÃ BỊ ADMIN KHÓA!</h2>
                <p style="color:#aaa;">Vui lòng liên hệ Admin After13Friday để biết thêm chi tiết.</p>
                <a href="/" style="color:#66fcf1; text-decoration:none;">Quay lại Trang chủ</a>
            </div>
            """

def load_interface_settings():
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    settings_dict = {row['key']: row['value'] for row in rows}
    
    theme_name = settings_dict.get('current_theme', 'peony-pink')
    theme_data = THEMES.get(theme_name, THEMES['peony-pink'])
    
    theme_data['announcement'] = settings_dict.get('announcement', '')
    theme_data['current_theme_name'] = theme_name
    return theme_data

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>After13Friday - Vũ Trụ Truyện</title>
    <style>
        body {
            margin: 0; font-family: 'Segoe UI', system-ui, sans-serif;
            background: {{ ui.bg }};
            background-image: {{ ui.bg_img }};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: {{ ui.text }}; min-height: 100vh; position: relative; overflow-x: hidden;
            transition: all 0.3s ease;
        }
        .starry-sky {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;
            background: radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
                        radial-gradient(#45f3ff, rgba(69,243,255,.1) 2px, transparent 20px);
            background-size: 550px 550px, 400px 400px; animation: blink 6s infinite ease-in-out alternate; 
            z-index: 1; opacity: {{ ui.star_opacity }};
        }
        @keyframes blink { 0% { opacity: 0.2; } 100% { opacity: 0.6; } }
        header {
            position: relative; z-index: 2; padding: 20px; text-align: center;
            background: {{ 'rgba(255, 255, 255, 0.85)' if ui.current_theme_name != 'cosmic-dark' else 'rgba(11, 12, 16, 0.7)' }};
            backdrop-filter: blur(10px); border-bottom: 1px solid {{ ui.border }};
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        header h1 { margin: 0; font-size: 2.2rem; color: {{ ui.primary }}; text-shadow: 0 0 5px {{ ui.primary }}44; }
        .nav-bar { margin-top: 15px; }
        .nav-link { color: {{ ui.text }}; text-decoration: none; margin: 0 12px; font-size: 0.95rem; font-weight: 500; }
        .nav-link:hover { color: {{ ui.primary }}; }
        .container { position: relative; z-index: 2; max-width: 1000px; margin: 30px auto; padding: 20px; box-sizing: border-box; }
        .card {
            background: {{ ui.card_bg }}; border: 1px solid {{ ui.border }};
            border-radius: 12px; padding: 25px; margin-bottom: 25px; backdrop-filter: blur(8px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        }
        .btn {
            background: {{ ui.primary }}; color: #fff; border: none;
            padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block;
            transition: opacity 0.2s;
        }
        .btn:hover { opacity: 0.9; }
        .btn-danger { background: #ff4d4d; color: #fff; }
        input, select {
            width: 100%; padding: 12px; margin: 10px 0 20px 0; 
            background: {{ '#fff' if ui.current_theme_name != 'cosmic-dark' else 'rgba(0,0,0,0.5)' }};
            border: 1px solid {{ ui.border }}; border-radius: 6px; color: {{ ui.text }}; box-sizing: border-box;
        }
        table { width: 100%; border-collapse: collapse; text-align: left; margin-top: 15px; }
        th, td { padding: 12px; border-bottom: 1px solid {{ ui.border }}; }
        th { color: {{ ui.primary }}; }
        .tag {
            background: {{ ui.accent }}; color: {{ ui.primary }};
            padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; display: inline-block; margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="starry-sky"></div>
    <header>
        <h1>🌌 AFTER 13 FRIDAY</h1>
        <p style="color: {{ ui.text_muted }}; margin: 5px 0;">{{ ui.announcement }}</p>
        <div class="nav-bar">
            <a class="nav-link" href="/">🏠 Trang Chủ</a>
            {% if session.get('user_id') %}
                <span style="color: {{ ui.primary }}; font-weight: bold; margin-right: 10px;">⭐ {{ session.get('stars') }} Sao</span>
                <a class="nav-link" href="/dashboard">✍️ Đăng Truyện (+20 Sao)</a>
                {% if session.get('role') == 'admin' %}
                    <a class="nav-link" style="color: #ff4545; font-weight: bold;" href="/admin/dashboard">👑 Quản Trị</a>
                {% endif %}
                <a class="nav-link" href="/logout" style="color: {{ ui.text_muted }};">Đăng Xuất ({{ session.get('username') }})</a>
            {% else %}
                <a class="nav-link" href="/login">🔑 Đăng Nhập</a>
                <a class="nav-link" href="/register" style="color: {{ ui.primary }};">📝 Đăng Ký (+50 Sao)</a>
            {% endif %}
        </div>
    </header>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    DictLoader({'base': BASE_LAYOUT})
])

@app.route('/')
def home():
    ui = load_interface_settings()
    db = get_db()
    if 'user_id' in session:
        u_data = db.execute("SELECT stars FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if u_data: session['stars'] = u_data['stars']
        
    stories_list = db.execute("SELECT * FROM stories ORDER BY id DESC").fetchall()
    
    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="text-align: center; border-left: 5px solid {{ ui.primary }};">
        <h2 style="margin: 0; color: {{ ui.primary }}; font-size: 1.8rem;">📚 Sảnh Truyện Vũ Trụ After13Friday</h2>
        <p style="margin: 5px 0 0 0; color: {{ ui.text_muted }};">Nền tảng đọc truyện tương tác thế hệ mới</p>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
        {% for story in stories %}
        <div class="card" style="margin-bottom: 0;">
            <h3 style="margin: 0 0 10px 0; color: {{ ui.primary }};">📖 {{ story.title }}</h3>
            <div style="margin-bottom: 12px;">
                <span class="tag">Ngôn Tình</span>
                <span class="tag">Truyện Dài</span>
            </div>
            <p style="margin: 5px 0; font-size: 0.9rem; color: {{ ui.text_muted }};">Tác giả: ✨ {{ story.author_name }}</p>
            <p style="margin: 5px 0; font-size: 0.9rem; color: {{ ui.text_muted }};">Thời lượng: {{ story.chapters }} chương</p>
            <p style="margin: 5px 0; font-size: 0.9rem; color: {{ ui.text_muted }};">Tương tác: 👁️ {{ story.views }} lượt xem</p>
            <p style="margin: 10px 0; font-weight: bold; color: {{ ui.primary }};">Phí đọc: 5 Sao</p>
            <a href="/read/{{ story.id }}" class="btn" style="font-size: 0.85rem; width: 100%; text-align: center; box-sizing: border-box;">Bấm Đọc Truyện</a>
        </div>
        {% else %}
        <p style="color: {{ ui.text_muted }}; text-align: center; grid-column: 1/-1;">Chưa có tác phẩm nào được đăng tải. Hãy là người đầu tiên sáng tác!</p>
        {% endfor %}
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui, stories=stories_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    ui = load_interface_settings()
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        if username and password:
            db = get_db()
            try:
                db.execute("INSERT INTO users (username, password, role, stars) VALUES (?, ?, 'user', 50)", (username, password))
                db.commit()
                return "<script>alert('Đăng ký thành công! Bạn nhận được 50 Sao làm quà tân thủ!'); window.location='/login';</script>"
            except sqlite3.IntegrityError:
                return "<script>alert('Tên tài khoản này đã có người sử dụng rồi!'); window.history.back();</script>"
    
    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="max-width: 450px; margin: 40px auto;">
        <h2 style="text-align: center; color: {{ ui.primary }}; margin-top: 0;">📝 Đăng Ký Tài Khoản</h2>
        <form method="POST">
            <label>Tên tài khoản mới:</label>
            <input type="text" name="username" required placeholder="Nhập tên tài khoản...">
            <label>Mật khẩu mật mã:</label>
            <input type="password" name="password" required placeholder="Nhập mật khẩu...">
            <button type="submit" class="btn" style="width: 100%;">Tạo Tài Khoản Nhận Khởi Nguyên Sao</button>
        </form>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ui = load_interface_settings()
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user:
            if user['is_blocked'] == 1:
                return "<script>alert('Tài khoản này đang bị khóa!'); window.history.back();</script>"
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['stars'] = user['stars']
            return redirect(url_for('home'))
        else:
            return "<script>alert('Sai tài khoản hoặc mật khẩu rồi bạn ơi!'); window.history.back();</script>"
            
    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="max-width: 450px; margin: 40px auto;">
        <h2 style="text-align: center; color: {{ ui.primary }}; margin-top: 0;">🔑 Đăng Nhập Hệ Thống</h2>
        <form method="POST">
            <label>Tên tài khoản:</label>
            <input type="text" name="username" required>
            <label>Mật khẩu:</label>
            <input type="password" name="password" required>
            <button type="submit" class="btn" style="width: 100%;">Đăng Nhập Khám Phá Vũ Trụ</button>
        </form>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    ui = load_interface_settings()
    
    if request.method == 'POST':
        title = request.form.get('title').strip()
        chapters = request.form.get('chapters')
        if title:
            db = get_db()
            db.execute("INSERT INTO stories (title, chapters, views, author_name) VALUES (?, ?, 0, ?)", (title, chapters, session['username']))
            db.execute("UPDATE users SET stars = stars + 20 WHERE id = ?", (session['user_id'],))
            db.commit()
            return "<script>alert('Đăng truyện thành công! Chúc mừng tác giả được cộng thêm +20 Sao!'); window.location='/';</script>"

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: {{ ui.primary }}; margin-top: 0;">✍️ Không Gian Sáng Tác Tác Giả</h2>
        <p style="color: {{ ui.text_muted }}; font-size: 0.9rem;">Mỗi lần phát hành một đầu truyện mới, hệ thống sẽ tự động thưởng cho bạn <b>+20 Sao</b>!</p>
        <form method="POST" style="margin-top: 20px;">
            <label>Tên tác phẩm truyện:</label>
            <input type="text" name="title" required placeholder="Nhập tên truyện của bạn...">
            <label>Số lượng chương khởi đầu:</label>
            <input type="number" name="chapters" value="1" min="1" required>
            <button type="submit" class="btn">🚀 Xuất Bản & Nhận Thưởng Sao</button>
        </form>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui)

@app.route('/read/<int:story_id>')
def read_story(story_id):
    if 'user_id' not in session: return "<script>alert('Vui lòng đăng nhập tài khoản trước khi đọc truyện nhé!'); window.location='/login';</script>"
    ui = load_interface_settings()
    db = get_db()
    
    story = db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
    if not story: return redirect(url_for('home'))
    
    user = db.execute("SELECT stars FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    if session['role'] != 'admin':
        if user['stars'] < 5:
            return "<script>alert('Úi! Bạn không đủ Sao rồi. Hãy đăng truyện mới để kiếm thêm Sao!'); window.location='/';</script>"
        
        db.execute("UPDATE users SET stars = stars - 5 WHERE id = ?", (session['user_id'],))
        db.execute("UPDATE stories SET views = views + 1 WHERE id = ?", (story_id,))
        db.execute("UPDATE users SET stars = stars + 1 WHERE id = ?", (session['user_id'],))
        db.execute("UPDATE users SET stars = stars + 2 WHERE username = ?", (story['author_name'],))
        db.commit()

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="text-align: center; max-width: 800px; margin: 0 auto; padding: 40px 30px;">
        <h1 style="color: {{ ui.primary }}; margin-top:0; font-size: 2.2rem;">{{ story.title }}</h1>
        <div style="margin: 15px 0;">
            <span class="tag">Vũ trụ ABO</span>
            <span class="tag">Tương lai</span>
            <span class="tag">Ngôn Tình</span>
        </div>
        <p style="color: {{ ui.text_muted }}; margin: 5px 0;"><strong>Tác giả:</strong> {{ story.author_name }}</p>
        <p style="color: {{ ui.text_muted }}; margin: 5px 0;"><strong>Thời lượng:</strong> {{ story.chapters }} Chương</p>
        
        <hr style="border: 0; border-top: 1px solid {{ ui.border }}; margin: 30px 0;">
        
        <h3 style="text-align: left; color: {{ ui.primary }};">📝 TÓM TẮT NỘI DUNG:</h3>
        <div style="font-size: 1.1rem; line-height: 1.8; text-align: left; color: {{ ui.text }}; padding: 10px 0;">
            Một câu tóm tắt: Pháo hoa chóng tàn... Nghĩa bóng là những thứ rực rỡ, nồng nhiệt nhưng ngắn ngủi, dễ phai tàn theo thời gian, thường dùng để nói về tình yêu...
            <br><br>
            💸 Độc giả đã trả phí 5 sao để mở khóa chương truyện thành công.
        </div>
        
        <h3 style="text-align: left; color: {{ ui.primary }}; border-bottom: 2px solid {{ ui.border }}; padding-bottom: 8px; margin-top: 40px;">📚 MỤC LỤC CÁC TẬP TRUYỆN</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-top: 15px; text-align: left;">
            <a href="#" style="background: {{ ui.card_bg }}; border: 1px solid {{ ui.border }}; color: {{ ui.text }}; padding: 12px; text-align: center; border-radius: 8px; text-decoration: none; font-weight: 500;">Giới Thiệu</a>
            {% for i in range(1, (story.chapters + 1)) %}
                <a href="#" style="background: {{ ui.card_bg }}; border: 1px solid {{ ui.border }}; color: {{ ui.text }}; padding: 12px; text-align: center; border-radius: 8px; text-decoration: none; font-weight: 500;">Chương {{ i }}</a>
            {% endfor %}
        </div>
        
        <a href="/" class="btn" style="margin-top: 40px;">➔ Trở về Sảnh Chung</a>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui, story=story)

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin': return "Quyền truy cập bị từ chối!", 403
    ui = load_interface_settings()
    db = get_db()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'toggle_block':
            user_id = request.form.get('user_id')
            current_status = int(request.form.get('current_status'))
            new_status = 1 if current_status == 0 else 0
            db.execute("UPDATE users SET is_blocked = ? WHERE id = ?", (new_status, user_id))
            db.commit()
            return redirect(url_for('admin_dashboard'))
            
        elif action == 'update_ui':
            theme_choice = request.form.get('theme_choice')
            announcement = request.form.get('announcement')
            
            db.execute("REPLACE INTO settings (key, value) VALUES ('current_theme', ?)", (theme_choice,))
            db.execute("REPLACE INTO settings (key, value) VALUES ('announcement', ?)", (announcement,))
            db.commit()
            return "<script>alert('Giao diện hệ thống đã được cập nhật thay đổi thành công!'); window.location='/admin/dashboard';</script>"
            
        elif action == 'change_password':
            new_password = request.form.get('new_password').strip()
            if new_password:
                db.execute("UPDATE users SET password = ? WHERE role = 'admin'", (new_password,))
                db.commit()
                return "<script>alert('Đổi mật khẩu Admin thành công! Vui lòng đăng nhập lại.'); window.location='/logout';</script>"

    users_list = db.execute("SELECT * FROM users WHERE role != 'admin'").fetchall()
    
    content = """
    {% extends "base" %}
    {% block content %}
    <h2 style="color: #ff4545;">👑 TỐI CAO PANEL - QUẢN TRỊ TRANG WEB</h2>
    
    <div class="card">
        <h3 style="color: {{ ui.primary }}; margin-top: 0;">🎨 Cấu Hình Bộ Màu Giao Diện</h3>
        <form method="POST">
            <input type="hidden" name="action" value="update_ui">
            
            <label style="font-weight: bold; display: block; margin-bottom: 10px;">Chọn bộ giao diện đại diện:</label>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <label style="background: rgba(0,0,0,0.05); padding: 12px; border-radius: 8px; cursor: pointer; display: flex; align-items: center;">
                    <input type="radio" name="theme_choice" value="peony-pink" style="width: auto; margin: 0 10px 0 0;" {% if ui.current_theme_name == 'peony-pink' %}checked{% endif %}>
                    🌸 Hoa Mẫu Đơn (Hồng Ngôn Tình)
                </label>
                <label style="background: rgba(0,0,0,0.05); padding: 12px; border-radius: 8px; cursor: pointer; display: flex; align-items: center;">
                    <input type="radio" name="theme_choice" value="light-green" style="width: auto; margin: 0 10px 0 0;" {% if ui.current_theme_name == 'light-green' %}checked{% endif %}>
                    🟢 Xanh Lá & Trắng (Nhã nhặn)
                </label>
                <label style="background: rgba(0,0,0,0.05); padding: 12px; border-radius: 8px; cursor: pointer; display: flex; align-items: center;">
                    <input type="radio" name="theme_choice" value="red-purple" style="width: auto; margin: 0 10px 0 0;" {% if ui.current_theme_name == 'red-purple' %}checked{% endif %}>
                    🔮 Đỏ & Tím (Huyền ảo)
                </label>
                <label style="background: rgba(0,0,0,0.05); padding: 12px; border-radius: 8px; cursor: pointer; display: flex; align-items: center;">
                    <input type="radio" name="theme_choice" value="cosmic-dark" style="width: auto; margin: 0 10px 0 0;" {% if ui.current_theme_name == 'cosmic-dark' %}checked{% endif %}>
                    🌌 Vũ Trụ Tối (Sao lấp lánh)
                </label>
            </div>

            <label>Lời thông báo chạy ở Header:</label>
            <input type="text" name="announcement" value="{{ ui.announcement }}" required>
            
            <button type="submit" class="btn">🎨 Áp Dụng Thay Đổi Toàn Hệ Thống</button>
        </form>
    </div>

    <div class="card">
        <h3 style="color: {{ ui.primary }}; margin-top: 0;">🔐 Đổi Mật Khẩu Admin Tối Cao</h3>
        <form method="POST">
            <input type="hidden" name="action" value="change_password">
            <label>Nhập mật khẩu mới muốn thay đổi:</label>
            <input type="text" name="new_password" placeholder="Nhập mật khẩu mới tại đây..." required>
            <button type="submit" class="btn" style="background: linear-gradient(45deg, #ff9900, #ff5500);">🔐 Cập Nhật Mật Khẩu Mới</button>
        </form>
    </div>

    <div class="card">
        <h3 style="color: {{ ui.primary }}; margin-top: 0;">👥 Danh Sách Người Dùng Hệ Thống</h3>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tên Tài Khoản</th>
                    <th>Số Sao</th>
                    <th>Trạng Thái</th>
                    <th>Hành Động</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.id }}</td>
                    <td style="font-weight:bold;">{{ user.username }}</td>
                    <td style="color:{{ ui.primary }}; font-weight: bold;">⭐ {{ user.stars }} Sao</td>
                    <td>
                        {% if user.is_blocked == 1 %}
                            <span style="color:#ff4d4d; font-weight:bold;">🚨 Bị Khóa</span>
                        {% else %}
                            <span style="color: green; font-weight: bold;">Hoạt Động</span>
                        {% endif %}
                    </td>
                    <td>
                        <form method="POST" style="margin:0; display:inline;">
                            <input type="hidden" name="action" value="toggle_block">
                            <input type="hidden" name="user_id" value="{{ user.id }}">
                            <input type="hidden" name="current_status" value="{{ user.is_blocked }}">
                            {% if user.is_blocked == 1 %}
                                <button type="submit" class="btn" style="padding: 5px 12px; font-size:0.8rem;">🔓 Mở Khóa</button>
                            {% else %}
                                <button type="submit" class="btn btn-danger" style="padding: 5px 12px; font-size:0.8rem;">🔒 Khóa</button>
                            {% endif %}
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui, users=users_list)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
