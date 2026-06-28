import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
# Thiết kế Theme "Anime Luxury"
THEME = {
    "bg": "#fff0f5",
    "card_bg": "rgba(255, 255, 255, 0.9)",
    "primary": "#d53f8c",
    "text": "#4a2c30",
    "font": "'Playfair Display', serif"
}

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@300&display=swap" rel="stylesheet">
    <style>
        body { background: {{ t.bg }}; font-family: 'Montserrat', sans-serif; color: {{ t.text }}; overflow-x: hidden; }
        
        /* Hiệu ứng cánh hoa rơi */
        .petal { position: fixed; top: -10px; z-index: 1; animation: fall linear infinite; color: #ff99cc; }
        @keyframes fall { to { transform: translateY(100vh) rotate(360deg); } }

        /* Khung nhân vật Anime trang trí */
        .anime-char { position: fixed; bottom: 0; width: 220px; z-index: 5; opacity: 0.8; }
        #char-left { left: 0; }
        #char-right { right: 0; }

        .card { background: {{ t.card_bg }}; border-radius: 30px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px; }
        .like-btn { font-size: 3rem; cursor: pointer; transition: 0.3s; }
        .like-btn:active { transform: scale(1.5); }
    </style>
</head>
<body>
    <!-- Cánh hoa rơi -->
    <script>
        for(let i=0; i<20; i++){
            let p = document.createElement('div');
            p.innerHTML = '🌸'; p.className = 'petal';
            p.style.left = Math.random()*100 + 'vw';
            p.style.animationDuration = (Math.random()*5 + 5) + 's';
            document.body.appendChild(p);
        }
    </script>

    <!-- Nhân vật Anime (Dùng ảnh minh họa phong cách Nhật) -->
    <img src="https://i.imgur.com/8Fk7L4k.png" class="anime-char" id="char-left">
    <img src="https://i.imgur.com/wVjHkZp.png" class="anime-char" id="char-right">

    <div style="max-width: 800px; margin: auto; position: relative; z-index: 10;">
        <h1 style="text-align: center; font-family: {{ t.font }}; color: {{ t.primary }};">After 13 Friday</h1>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    content = """
    {% extends "base" %}
    {% block content %}
    <div class="card" style="text-align: center;">
        <h2>Chào mừng đến với không gian truyện Anime</h2>
        <div class="like-btn" onclick="bloom()">🌸</div>
        <p id="count">Lượt thích: 0</p>
    </div>
    <script>
        let c = 0;
        function bloom() {
            c++;
            document.getElementById('count').innerText = 'Lượt thích: ' + c;
            alert('Hoa đã nở rộ vì bạn!');
        }
    </script>
    {% endblock %}
    """
    return render_template_string(content, t=THEME)

app.jinja_loader = ChoiceLoader([app.jinja_loader, DictLoader({'base': BASE_LAYOUT})])

if __name__ == '__main__':
    app.run(debug=True)
