import os
import sqlite3
from flask import Flask, request, redirect, url_for, session, render_template_string, flash

app = Flask(__name__)
app.secret_key = "after13friday_cosmic_secret_key"
DATABASE = "database.db"

# 🛠️ KHỞI TẠO CƠ SỞ DỮ LIỆU TỰ ĐỘNG
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        # 1. Bảng thành viên (Tài khoản, Vai trò, Số Sao, Trạng thái khóa)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            stars INTEGER DEFAULT 50,
            is_blocked INTEGER DEFAULT 0
        )""")
        # 2. Bảng tác phẩm truyện
        conn.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            chapters INTEGER DEFAULT 1,
            views INTEGER DEFAULT 0,
            author_name TEXT NOT NULL,
            star_cost INTEGER DEFAULT 5
        )""")
        # 3. Bảng cấu hình giao diện tùy chỉnh của Admin
        conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        
        # Tạo tài khoản Tối cao của Admin mặc định nếu chưa tồn tại
        try:
            conn.execute("INSERT INTO users (username, password, role, stars) VALUES ('admin', 'admin123', 'admin', 999999)")
        except sqlite3.IntegrityError:
            pass
            
        # Cấu hình giao diện mặc định ban đầu
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('primary_color', '#66fcf1')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('bg_gradient', 'linear-gradient(135deg, #06060c, #110e26, #1b163a)')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('announcement', 'Nơi những câu chuyện chạm đến tận cùng cảm xúc')")
        conn.commit()

init_db()

# 🔐 KIỂM TRA TRẠNG THÁI KHÓA TÀI KHOẢN TRƯỚC MỖI LƯỢT TRUY CẬP
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

# 🎨 HÀM ĐỌC CẤU HÌNH GIAO DIỆN ĐỘNG
def load_interface_settings():
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    return {row['key']: row['value'] for row in rows}

# 🌌 KHUNG GIAO DIỆN CHUẨN (SAO LẤP LÁNH)
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>After13Friday - Vũ Trụ Truyện</title>
    <style>
        body {
            margin: 0; font-family: 'Segoe UI', sans-serif;
            background: {{ ui.bg_gradient }}; color: #c5c6c7; min-height: 100vh; position: relative; overflow-x: hidden;
        }
        .starry-sky {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;
            background: radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
                        radial-gradient(#45f3ff, rgba(69,243,255,.1) 2px, transparent 20px);
            background-size: 550px 550px, 400px 400px; animation: blink 6s infinite ease-in-out alternate; z-index: 1; opacity: 0.5;
        }
        @keyframes blink { 0% { opacity: 0.3; transform: scale(0.98); } 100% { opacity: 0.8; transform: scale(1.02); } }
        header {
            position: relative; z-index: 2; padding: 20px; text-align: center;
            background: rgba(11, 12, 16, 0.7); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        header h1 { margin: 0; font-size: 2.2rem; color: {{ ui.primary_color }}; text-shadow: 0 0 10px {{ ui.primary_color }}; }
        .nav-bar { margin-top: 15px; }
        .nav-link { color: #fff; text-decoration: none; margin: 0 12px; font-size: 0.95rem; }
        .nav-link:hover { color: {{ ui.primary_color }}; }
        .container { position: relative; z-index: 2; max-width: 1000px; margin: 30px auto; padding: 20px; box-sizing: border-box; }
        .card {
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px; padding: 25px; margin-bottom: 25px; backdrop-filter: blur(5px);
        }
        .btn {
            background: linear-gradient(45deg, #00f2fe, #4facfe); color: #000; border: none;
            padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block;
        }
        .btn-danger { background: linear-gradient(45deg, #ff416c, #ff4b2b); color: #fff; }
        input, select {
            width: 100%; padding: 12px; margin: 10px 0 20px 0; background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; color: #fff; box-sizing: border-box;
        }
    </style>
</head>
<body>
    <div class="starry-sky"></div>
    <header>
        <h1>🌌 AFTER 13 FRIDAY</h1>
        <p style="color: #888; margin: 5px 0;">{{ ui.announcement }}</p>
        <div class="nav-bar">
            <a class="nav-link" href="/">🏠 Trang Chủ</a>
            {% if session.get('user_id') %}
                <span style="color: #fffb00; font-weight: bold; margin-right: 10px;">⭐ {{ session.get('stars') }} Sao</span>
                <a class="nav-link" href="/dashboard">✍️ Đăng Truyện (+20 Sao)</a>
                {% if session.get('role') == 'admin' %}
                    <a class="nav-link" style="color: #ff4545; font-weight: bold;" href="/admin/dashboard">👑 Quản Trị Hệ Thống</a>
                {% endif %}
                <a class="nav-link" href="/logout" style="color: #aaa;">Đăng Xuất ({{ session.get('username') }})</a>
            {% else %}
                <a class="nav-link" href="/login">🔑 Đăng Nhập</a>
                <a class="nav-link" href="/register" style="color: {{ ui.primary_color }};">📝 Đăng Ký (+50 Sao)</a>
            {% endif %}
        </div>
    </header>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# 🏠 TRANG CHỦ LỆNH HIỂN THỊ
@app.route('/')
def home():
    ui = load_interface_settings()
    db = get_db()
    # Cập nhật lại số sao thực tế trong session nếu đã đăng nhập
    if 'user_id' in session:
        u_data = db.execute("SELECT stars FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if u_data: session['stars'] = u_data['stars']
        
    stories_list = db.execute("SELECT * FROM stories ORDER BY id DESC").fetchall()
    
    content = """
    {% extends "base" %}
    {% block content %}
    <h2 style="color: #fff; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">📚 Sảnh Truyện Vũ Trụ NovelToon</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px;">
        {% for story in stories %}
        <div class="card">
            <h3 style="margin: 0 0 10px 0; color: {{ ui.primary_color }};">📖 {{ story.title }}</h3>
            <p style="margin: 5px 0; font-size: 0.9rem; color: #aaa;">Tác giả: ✨ {{ story.author_name }}</p>
            <p style="margin: 5px 0; font-size: 0.9rem; color: #aaa;">Thời lượng: {{ story.chapters }} chương</p>
            <p style="margin: 5px 0; font-size: 0.9rem; color: #aaa;">Tương tác: 👁️ {{ story.views }} lượt xem</p>
            <p style="margin: 10px 0; font-weight: bold; color: #fffb00;">Phí đọc: 5 Sao</p>
            <a href="/read/{{ story.id }}" class="btn" style="font-size: 0.85rem; width: 100%; text-align: center; box-sizing: border-box;">Bấm Đọc Truyện</a>
        </div>
        {% else %}
        <p style="color: #888;">Chưa có tác phẩm nào được đăng tải. Hãy là người đầu tiên sáng tác!</p>
        {% endfor %}
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui, stories=stories_list)

# 📝 ĐĂNG KÝ THÀNH VIÊN MỚI
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
        <h2 style="text-align: center; color: #fff; margin-top: 0;">📝 Đăng Ký Tài Khoản</h2>
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

# 🔑 ĐĂNG NHẬP
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
        <h2 style="text-align: center; color: #fff; margin-top: 0;">🔑 Đăng Nhập Hệ Thống</h2>
        <form method="POST">
            <label>Tên tài khoản:</label>
            <input type="text" name="username" required>
            <label>Mật khẩu:</label>
            <input type="password" name="password" required>
            <button type="submit" class="btn" style="width: 100%;">Đăng Nhập Khám Phá Vũ Trụ</button>
        </form>
        <p style="text-align: center; font-size: 0.85rem; margin-top: 15px;">Mặc định Admin: tài khoản <b>admin</b> / mật khẩu <b>admin123</b></p>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui)

# 🚪 ĐĂNG XUẤT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ✍️ DASHBOARD: ĐĂNG TRUYỆN DÀNH CHO TÁC GIẢ
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    ui = load_interface_settings()
    
    if request.method == 'POST':
        title = request.form.get('title').strip()
        chapters = request.form.get('chapters')
        if title:
            db = get_db()
            # Thêm truyện vào bảng danh sách
            db.execute("INSERT INTO stories (title, chapters, views, author_name) VALUES (?, ?, 0, ?)", (title, chapters, session['username']))
            # Tặng 20 Sao cho Tác giả vì đã đóng góp sáng tác sáng tạo
            db.execute("UPDATE users SET stars = stars + 20 WHERE id = ?", (session['user_id'],))
            db.commit()
            return "<script>alert('Đăng truyện thành công! Chúc mừng tác giả được cộng thêm +20 Sao!'); window.location='/';</script>"

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: #fff; margin-top: 0;">✍️ Không Gian Sáng Tác Tác Giả</h2>
        <p style="color: #45f3ff; font-size: 0.9rem;">Mỗi lần phát hành một đầu truyện mới, hệ thống sẽ tự động thưởng cho bạn <b>+20 Sao</b>!</p>
        <form method="POST" style="margin-top: 20px;">
            <label>Tên tác phẩm truyện (Ví dụ: Phúc Thần Ban Phước...):</label>
            <input type="text" name="title" required placeholder="Nhập tên truyện của bạn...">
            <label>Số lượng chương khởi đầu:</label>
            <input type="number" name="chapters" value="1" min="1" required>
            <button type="submit" class="btn">🚀 Xuất Bản & Nhận Thưởng Sao</button>
        </form>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui)

# 📖 HÀNH VI ĐỌC TRUYỆN TRỪ SAO VÀ TÍCH ĐIỂM FAN
@app.route('/read/<int:story_id>')
def read_story(story_id):
    if 'user_id' not in session: return "<script>alert('Vui lòng đăng nhập tài khoản trước khi đọc truyện nhé!'); window.location='/login';</script>"
    ui = load_interface_settings()
    db = get_db()
    
    # Lấy thông tin truyện
    story = db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
    if not story: return redirect(url_for('home'))
    
    # Kiểm tra số sao hiện có của độc giả
    user = db.execute("SELECT stars FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Nếu là Admin thì đọc miễn phí, nếu là User thường thì kiểm tra điểm sao
    if session['role'] != 'admin':
        if user['stars'] < 5:
            return "<script>alert('Úi! Bạn không đủ Sao rồi. Hãy đăng truyện mới để kiếm thêm Sao hoặc đăng ký tài khoản khác nha!'); window.location='/';</script>"
        
        # Đủ sao: Trừ độc giả 5 sao, Tăng lượt xem lên 1
        db.execute("UPDATE users SET stars = stars - 5 WHERE id = ?", (session['user_id'],))
        db.execute("UPDATE stories SET views = views + 1 WHERE id = ?", (story_id,))
        
        # Thưởng điểm cho fan: Độc giả đọc truyện sẽ được hệ thống tặng lại tinh tú +1 Sao (Kiếm Sao khi đọc)
        db.execute("UPDATE users SET stars = stars + 1 WHERE id = ?", (session['user_id'],))
        
        # Tặng điểm cho tác giả của bộ truyện đó (+2 Sao vì có fan xem)
        db.execute("UPDATE users SET stars = stars + 2 WHERE username = ?", (story['author_name'],))
        db.commit()

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="text-align: center; max-width: 700px; margin: 0 auto; padding: 50px 30px;">
        <h2 style="color: var(--primary-color); margin-top:0;">📖 ĐANG ĐỌC: {{ story.title }}</h2>
        <p style="color: #888;">Tác giả: {{ story.author_name }} | Thời lượng: {{ story.chapters }} Chương</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 30px 0;">
        <div style="font-size: 1.15rem; line-height: 1.8; text-align: left; color: #fff; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 8px;">
            🌌 [Nội dung chương truyện đang được cập nhật phát triển tiếp theo]... <br><br>
            Hệ thống NovelToon After13Friday đã ghi nhận tương tác thành công!<br>
            💸 Độc giả bị trừ 5 sao, được hoàn trả lại <b>+1 Sao tích điểm Fan</b>.<br>
            🎁 Tác giả sáng tác bộ truyện này nhận được hưởng <b>+2 Sao bản quyền</b> thành công!
        </div>
        <a href="/" class="btn" style="margin-top: 30px;">➔ Trở về sảnh sảnh chung</a>
    </div>
    {% endblock %}
    """
    return render_template_string(content, ui=ui, story=story)

# 👑 BỘ CHỈ HUY TỐI CAO: CHỈ DÀNH RIÊNG CHO ACCOUNT ADMIN
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin': return "Quyền truy cập bị từ chối!", 403
    ui = load_interface_settings()
    db = get_db()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Thao tác 1: Khóa / Mở khóa tài khoản thành viên
        if action == 'toggle_block':
            user_id = request.form.get('user_id')
            current_status = int(request.form.get('current_status'))
            new_status = 1 if current_status == 0 else 0
            db.execute("UPDATE users SET is_blocked = ? WHERE id = ?", (new_status, user_id))
            db.commit()
            return redirect(url_for('admin_dashboard'))
            
        # Thao tác 2: Chỉnh sửa màu sắc giao diện theo sở thích
        elif action == 'update_ui':
            primary = request.form.get('primary_color')
            bg = request.form.get('bg_gradient')
            announcement = request.form.get('announcement')
            
            db.execute("UPDATE settings SET value = ? WHERE key = 'primary_color'", (primary,))
            db.execute("UPDATE settings SET value = ? WHERE key = 'bg_gradient'", (bg,))
            db.execute("UPDATE settings SET value = ? WHERE key = 'announcement'", (announcement,))
            db.commit()
            return "<script>alert('Giao diện hệ thống đã được cập nhật thay đổi hoàn toàn!'); window.location='/admin/dashboard';</script>"

    users_list = db.execute("SELECT * FROM users WHERE role != 'admin'").fetchall()
    
    content = """
    {% extends "base" %}
    {% block content %}
    <h2 style="color: #ff4545;">👑 TỐI CAO PANEL - QUẢN TRỊ TRANG WEB</h2>
    
    <!-- 1. KHUNG CHỈNH SỬA GIAO DIỆN WED -->
    <div class="card">
        <h3 style="color: #66fcf1; margin-top: 0;">🎨 Tùy Biến Giao Diện Vũ Trụ</h3>
        <form method="POST">
            <input type="hidden" name="action" value="update_ui">
            <label>Màu chủ đạo Neon (Mã màu HEX hoặc tên màu):</label>
            <input type="text" name="primary_color" value="{{ ui.primary_color }}" required>
            <label>Hiệu ứng màu nền (CSS Gradient / Background):</label>
            <input type="text" name="bg_gradient" value="{{ ui.bg_gradient }}" required>
            <label>Lời thông báo chạy ở Header:</label>
            <input type="text" name="announcement" value="{{ ui.announcement }}" required>
            <button type="submit" class="btn">🎨 Áp Dụng Thay Đổi To Toàn Web</button>
        </form>
    </div>

    <!-- 2. QUẢN LÝ THÀNH VIÊN & KHÓA NICK -->
    <div class="card">
        <h3 style="color: #66fcf1; margin-top: 0;">👥 Danh Sách Người Dùng Hệ Thống</h3>
        <table style="width:100%; border-collapse: collapse; text-align: left; margin-top:15px;">
            <thead>
                <tr style="border-bottom: 2px solid rgba(255,255,255,0.1); color: #45f3ff;">
                    <th style="padding:10px;">ID</th>
                    <th>Tên Tài Khoản</th>
                    <th>Số Sao</th>
                    <th>Trạng Thái</th>
                    <th>Hành Động Quyền Lực</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px 10px;">{{ user.id }}</td>
                    <td style="font-weight:bold; color:#fff;">{{ user.username }}</td>
                    <td style="color:#fffb00;">⭐ {{ user.stars }} Sao</td>
                    <td>
                        {% if user.is_blocked == 1 %}
                            <span style="color:#ff4d4d; font-weight:bold;">🚨 Bị Khóa</span>
                        {% else %}
                            <span style="color:#45f3ff;">Hoạt Động</span>
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
                                <button type="submit" class="btn btn-danger" style="padding: 5px 12px; font-size:0.8rem;">🔒 Khóa Tài Khoản</button>
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

# ĐĂNG KÝ LAYOUT GỐC VÀO FLASK TEMPLATE CACHE
@app.before_request
def register_base_template():
    app.jinja_env.from_string(BASE_LAYOUT).name = "base"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
