import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Danh sách truyện mẫu hiển thị trên giao diện chính
    stories = [
        {"title": "Hành Trình Khởi Nguyên", "chapters": 24, "views": "1,520"},
        {"title": "Bão Đêm Thứ Sáu", "chapters": 13, "views": "890"},
        {"title": "Mùa Thu Đã Qua", "chapters": 8, "views": "410"}
    ]
    return render_template('index.html', title="After13Friday", stories=stories)

@app.route('/admin/dashboard')
def admin_dashboard():
    return """
    <div style="background:#0f0c1b; color:#fff; min-height:100vh; padding:40px; font-family:sans-serif; text-align:center;">
        <h1 style="color:#66fcf1; text-shadow: 0 0 10px #66fcf1;">👑 TRANG QUẢN TRỊ AFTER13FRIDAY</h1>
        <p style="color:#45f3ff;">Chào mừng Admin! Không gian quản lý dữ liệu tối cao của bạn đã sẵn sàng trực tuyến.</p>
    </div>
    """

if __name__ == '__main__':
    # Tự động nhận diện cổng mạng của Render hoặc mặc định là 5000 khi chạy máy cá nhân/Colab
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
