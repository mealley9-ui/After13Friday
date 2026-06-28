from flask import Flask, render_template_string

app = Flask(__name__)

# Giao diện Dark Glass (Kính mờ, sang trọng, không quê)
FULL_UI = """
<!DOCTYPE html>
<html>
<head>
    <style>
        :root { --glass: rgba(255, 255, 255, 0.05); --pink: #ff7eb3; }
        body { 
            margin: 0; background: #0a0a0a; color: white;
            font-family: 'Segoe UI', sans-serif; overflow-x: hidden;
            background: radial-gradient(circle at top right, #2a0845, #0a0a0a);
        }
        /* Hiệu ứng cánh hoa */
        .petal { position: fixed; color: var(--pink); z-index: 100; animation: fall linear infinite; pointer-events: none; }
        @keyframes fall { from { transform: translateY(-10vh); } to { transform: translateY(110vh) rotate(360deg); } }
        
        /* Glassmorphism Card */
        .glass-card {
            background: var(--glass); backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 20px;
            padding: 30px; margin: 20px; transition: 0.5s;
        }
        .glass-card:hover { transform: translateY(-10px); border-color: var(--pink); }
        
        /* Like button bung tỏa */
        .btn-like { cursor: pointer; padding: 15px 30px; background: var(--pink); border-radius: 50px; border: none; font-weight: bold; }
        .btn-like:active { transform: scale(0.9); }
    </style>
</head>
<body>
    <script>
        setInterval(() => {
            let p = document.createElement('div');
            p.innerHTML = '🌸'; p.className = 'petal';
            p.style.left = Math.random()*100 + 'vw';
            p.style.animationDuration = (Math.random()*3 + 3) + 's';
            document.body.appendChild(p);
            setTimeout(() => p.remove(), 5000);
        }, 500);
    </script>

    <div style="max-width: 800px; margin: auto; padding-top: 50px;">
        <h1 style="text-align:center; font-size: 3rem; background: linear-gradient(to right, #ff7eb3, #ff758c); -webkit-background-clip: text; color: transparent;">
            AFTER 13 FRIDAY
        </h1>
        
        <div class="glass-card">
            <h2>✨ Chào mừng Admin</h2>
            <p>Không gian quản lý dữ liệu tối cao đã sẵn sàng.</p>
            <button class="btn-like" onclick="alert('Đã thích! 🌸')">🌸 Thích Trang</button>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(FULL_UI)

if __name__ == '__main__':
    app.run(debug=True)
