```python
# ==========================================================
# AFTER 13 FRIDAY
# app.py
#
# Framework : Flask
# Database  : SQLite
#
# Nguồn tham khảo:
# 1. Flask Official Documentation
#    https://flask.palletsprojects.com/
#
# 2. Python sqlite3 Documentation
#    https://docs.python.org/3/library/sqlite3.html
#
# 3. Werkzeug Documentation
#    https://werkzeug.palletsprojects.com/
#
# 4. Miguel Grinberg
#    Flask Web Development (O'Reilly)
#
# ==========================================================

import os
import sqlite3
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from werkzeug.utils import secure_filename

# ==========================================================
# APP CONFIG
# ==========================================================

app = Flask(__name__)

app.secret_key = "after13friday_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

# ==========================================================
# CREATE FOLDER
# ==========================================================

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

# ==========================================================
# DATABASE
# ==========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================================
# INIT DATABASE
# ==========================================================

def init_db():

    conn = get_db()

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS story(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT NOT NULL,

        author TEXT NOT NULL,

        editor TEXT,

        category TEXT,

        summary TEXT,

        content TEXT,

        cover TEXT,

        status TEXT,

        views INTEGER DEFAULT 0,

        created_at TEXT

    )

    """)

    conn.commit()

    conn.close()

# ==========================================================
# FILE CHECK
# ==========================================================

def allowed_file(filename):

    return (

        "." in filename

        and

        filename.rsplit(".", 1)[1].lower()

        in ALLOWED_EXTENSIONS

    )

# ==========================================================
# SAVE IMAGE
# ==========================================================

def save_cover(file):

    if file.filename == "":

        return ""

    if not allowed_file(file.filename):

        return ""

    filename = secure_filename(file.filename)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    filename = f"{timestamp}_{filename}"

    path = os.path.join(

        app.config["UPLOAD_FOLDER"],

        filename

    )

    file.save(path)

    return filename

# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def home():

    conn = get_db()

    stories = conn.execute("""

        SELECT *

        FROM story

        ORDER BY id DESC

    """).fetchall()

    conn.close()

    return render_template(

        "index.html",

        stories=stories

    )

# ==========================================================
# ADD STORY
# ==========================================================

@app.route(
    "/add",
    methods=["GET", "POST"]
)

def add_story():

    if request.method == "POST":

        title = request.form.get("title")

        author = request.form.get("author")

        editor = request.form.get("editor")

        category = request.form.get("category")

        summary = request.form.get("summary")

        content = request.form.get("content")

        status = request.form.get("status")

        cover = request.files.get("cover")

        if title == "" or author == "":

            flash("Tên truyện và tác giả không được để trống.")

            return redirect(
                url_for("add_story")
            )

        filename = ""

        if cover:

            filename = save_cover(cover)

```python
        conn = get_db()

        conn.execute(

            """

            INSERT INTO story(

                title,

                author,

                editor,

                category,

                summary,

                content,

                cover,

                status,

                created_at

            )

            VALUES(

                ?,?,?,?,?,?,?,?,?

            )

            """,

            (

                title,

                author,

                editor,

                category,

                summary,

                content,

                filename,

                status,

                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )

            )

        )

        conn.commit()

        conn.close()

        flash(

            "✨ Thêm truyện thành công!",

            "success"

        )

        return redirect(

            url_for("home")

        )

    return render_template(

        "add_story.html"

    )

# ==========================================================
# STORY DETAIL
# ==========================================================

@app.route("/story/<int:story_id>")

def story_detail(story_id):

    conn = get_db()

    conn.execute(

        """

        UPDATE story

        SET views = views + 1

        WHERE id = ?

        """,

        (

            story_id,

        )

    )

    conn.commit()

    story = conn.execute(

        """

        SELECT *

        FROM story

        WHERE id = ?

        """,

        (

            story_id,

        )

    ).fetchone()

    conn.close()

    if story is None:

        abort(404)

    return render_template(

        "detail.html",

        story=story

    )

# ==========================================================
# DELETE STORY
# ==========================================================

@app.route("/delete/<int:story_id>")

def delete_story(story_id):

    conn = get_db()

    story = conn.execute(

        """

        SELECT *

        FROM story

        WHERE id = ?

        """,

        (

            story_id,

        )

    ).fetchone()

    if story:

        if story["cover"]:

            image_path = os.path.join(

                app.config["UPLOAD_FOLDER"],

                story["cover"]

            )

            if os.path.exists(image_path):

                os.remove(image_path)

        conn.execute(

            """

            DELETE FROM story

            WHERE id = ?

            """,

            (

                story_id,

            )

        )

        conn.commit()

    conn.close()

    flash(

        "🗑️ Xóa truyện thành công.",

        "info"

    )

    return redirect(

        url_for("home")

    )

# ==========================================================
# EDIT STORY
# ==========================================================

@app.route(

    "/edit/<int:story_id>",

    methods=["GET", "POST"]

)

def edit_story(story_id):

    conn = get_db()

    story = conn.execute(

        """

        SELECT *

        FROM story

        WHERE id = ?

        """,

        (

            story_id,

        )

    ).fetchone()

    if story is None:

        conn.close()

        abort(404)

    if request.method == "POST":

        title = request.form.get("title")

        author = request.form.get("author")

        editor = request.form.get("editor")

        category = request.form.get("category")

        summary = request.form.get("summary")

        content = request.form.get("content")

        status = request.form.get("status")

        cover = request.files.get("cover")

        filename = story["cover"]

        if cover and cover.filename != "":

            filename = save_cover(cover)

```python
        conn.execute(

            """

            UPDATE story

            SET

                title = ?,

                author = ?,

                editor = ?,

                category = ?,

                summary = ?,

                content = ?,

                cover = ?,

                status = ?

            WHERE id = ?

            """,

            (

                title,

                author,

                editor,

                category,

                summary,

                content,

                filename,

                status,

                story_id

            )

        )

        conn.commit()

        conn.close()

        flash(

            "✏️ Cập nhật truyện thành công!",

            "success"

        )

        return redirect(

            url_for(

                "story_detail",

                story_id=story_id

            )

        )

    conn.close()

    return render_template(

        "edit_story.html",

        story=story

    )

# ==========================================================
# SEARCH
# ==========================================================

@app.route("/search")

def search():

    keyword = request.args.get(

        "keyword",

        ""

    )

    conn = get_db()

    stories = conn.execute(

        """

        SELECT *

        FROM story

        WHERE

            title LIKE ?

            OR

            author LIKE ?

            OR

            category LIKE ?

        ORDER BY id DESC

        """,

        (

            f"%{keyword}%",

            f"%{keyword}%",

            f"%{keyword}%"

        )

    ).fetchall()

    conn.close()

    return render_template(

        "index.html",

        stories=stories,

        keyword=keyword

    )

# ==========================================================
# CATEGORY
# ==========================================================

@app.route("/category/<string:name>")

def category(name):

    conn = get_db()

    stories = conn.execute(

        """

        SELECT *

        FROM story

        WHERE category = ?

        ORDER BY id DESC

        """,

        (

            name,

        )

    ).fetchall()

    conn.close()

    return render_template(

        "index.html",

        stories=stories,

        keyword=name

    )

# ==========================================================
# ERROR PAGE
# ==========================================================

@app.errorhandler(404)

def page_not_found(error):

    return render_template(

        "404.html"

    ), 404

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    init_db()

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )

