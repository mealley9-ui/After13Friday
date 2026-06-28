import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 📚 Danh sách truyện dùng chung cho toàn hệ thống (Biến toàn cục)
stories = [
    {"title": "Hành Trình Khởi Nguyên", "chapters": 24, "views": "1,520"},
    {"title": "Bão Đêm Thứ Sáu", "chapters": 13, "views": "890"},
    {"title": "Mùa Thu Đã Qua", "chapters": 8, "views": "410"}
]

@app.route('/')
def home():
    return render_template('index.html', title="After13Friday", stories=stories)

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        # Lấy dữ liệu từ Form người dùng nhập vào
        title = request.form.get('title')
        chapters = request.form.get('chapters')
        views = request.form.get('views')
        
        if title and chapters and views:
            # Tiến hành thêm bộ truyện mới vào danh sách hiển thị
            stories.append({
                "title": title,
                "chapters": int(chapters),
                "views": views
            })
        # Thêm xong thì tự động tải lại trang admin để cập nhật bảng
        return redirect(url_for('admin_dashboard'))

    # Giao diện HTML sắc nét của trang quản trị tối cao Admin
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trang Quản Trị - After13Friday</title>
        <style>
            body {
                background: #0f0c1b;
                color: #fff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px 20px;
            }
            .container {
                max-width: 850px;
                margin: 0 auto;
            }
            h1 {
                color: #66fcf1;
                text-shadow: 0 0 10px rgba(102, 252, 241, 0.5);
                text-align: center;
                margin-bottom: 35px;
                font-size: 2rem;
            }
            .card {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
            }
            .card-title {
                color: #45f3ff;
                font-size: 1.2rem;
                margin-top: 0;
                margin-bottom: 20px;
                border-bottom: 1px solid rgba(69, 243, 255, 0.2);
                padding-bottom: 10px;
                font-weight: 600;
            }
            .form-group {
                margin-bottom: 18px;
            }
            label {
                display: block;
                margin-bottom: 6px;
                color: #ccc;
                font-size: 0.9rem;
            }
            input {
                width: 100%;
                padding: 12px;
                background: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: #fff;
                box-sizing: border-box;
                font-size: 0.95rem;
            }
            input:focus {
                border-color: #66fcf1;
                outline: none;
                box-shadow: 0 0 8px rgba(102, 252, 241, 0.3);
            }
            .form-row {
                display: flex;
                gap: 20px;
            }
            .form-row .form-group {
                flex: 1;
            }
            button {
                background: linear-gradient(45deg, #00f2fe, #4facfe);
                color: #0d0b18;
                border: none;
                padding: 14px 20px;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                font-size: 1rem;
                transition: 0.3s ease;
                margin-top: 5px;
            }
            button:hover {
                opacity: 0.95;
                box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
                transform: translateY(-1px);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                padding: 14px 16px;
                text-align: left;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }
            th {
                color: #66fcf1;
                background: rgba(102, 252, 241, 0.08);
                font-weight: 600;
            }
            td {
                font-size: 0.95rem;
            }
            tr:hover {
                background: rgba(255, 255, 255, 0.02);
            }
            .footer-links {
                text-align: center;
                margin-top: 25px;
            }
            .btn-link {
                color: #66fcf1;
                text-decoration: none;
                font-size: 0.95rem;
            }
            .btn-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👑 VŨ TRỤ TRUYỆN - TRANG QUẢN TRỊ</h1>
            
            <div class="card">
                <div class="card-title">✨ Đăng Tác Phẩm Truyện Mới</div>
                <form method="POST">
                    <div class="form-group">
                        <label>Tên tác phẩm / Tên truyện:</label>
                        <input type="text" name="title" placeholder="Nhập tên truyện (Ví dụ: Phúc Thần Ban Phước...)" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Số chương hiện tại:</label>
                            <input type="number" name="chapters" placeholder="Ví dụ: 30" required>
                        </div>
                        <div class="form-group">
                            <label>Lượt xem ảo ban đầu:</label>
                            <input type="text" name="views" placeholder="Ví dụ: 2,450" required>
                        </div>
                    </div>
                    <button type="submit">🚀 Phát Hành Lên Trang Chủ</button>
                </form>
            </div>

            <div class="card">
                <div class="card-title">📚 Các Truyện Đang Hiển Thị Trên Web</div>
                <table>
                    <thead>
                        <tr>
                            <th>Tên Tác Phẩm</th>
                            <th>Thời Lượng</th>
                            <th>Số Lượt Xem</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for story in stories:
        html_content += f"""
                        <tr>
                            <td style="font-weight: 500; color: #45f3ff;">{story['title']}</td>
                            <td>{story['chapters']} chương</td>
                            <td style="color: #bbb;">✨ {story['views']} lượt xem</td>
                        </tr>
        """
        
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="footer-links">
                <a href="/" class="btn-link" target="_blank">➔ Quay lại kiểm tra giao diện Độc giả</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
