import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "mangas.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

VALID_STATUSES = ["読みたい", "読書中", "読了", "中断中", "断念"]
STATUS_CLASSES = {
    "読みたい": "to-read",
    "読書中": "reading",
    "読了": "completed",
    "中断中": "on-hold",
    "断念": "dropped",
}

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-school-project-manga-list"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max per upload

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Database

def connect_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row  # access columns by name
    return connection


def init_db():
    connection = connect_db()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()


def db_ready():
    # checks the mangas table really exists, not just the .db file
    if not os.path.exists(DATABASE):
        return False
    connection = sqlite3.connect(DATABASE)
    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='mangas'"
    ).fetchone()
    connection.close()
    return table is not None


#  Validation

TITLE_REGEX = re.compile(r"^.{1,150}$")
AUTHOR_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ぀-ヿ一-鿿' \-.]{1,100}$")
RATING_REGEX = re.compile(r"^([0-9](\.[0-9]{1,2})?|10(\.0{1,2})?)$")
POSITIVE_INT_REGEX = re.compile(r"^[0-9]{1,5}$")
IMAGE_EXTENSION_REGEX = re.compile(r"^.+\.(png|jpg|jpeg|gif|webp)$", re.IGNORECASE)


def file_allowed(file_name):
    return bool(file_name) and bool(IMAGE_EXTENSION_REGEX.match(file_name))


def validate_form(form):
    errors = []

    title = form.get("title", "").strip()
    if not TITLE_REGEX.match(title):
        errors.append("タイトルは必須です(150文字以内で入力してください)。")

    author = form.get("author", "").strip()
    if not AUTHOR_REGEX.match(author):
        errors.append("作者は必須です(文字・スペース・アポストロフィ・ハイフンのみ使用できます)。")

    status = form.get("status", "").strip()
    if status not in VALID_STATUSES:
        errors.append("選択されたステータスが正しくありません。")

    volumes_owned = (form.get("volumes_owned", "0") or "0").strip()
    if not POSITIVE_INT_REGEX.match(volumes_owned):
        errors.append("所有冊数は0以上の整数で入力してください。")

    volumes_read = (form.get("volumes_read", "0") or "0").strip()
    if not POSITIVE_INT_REGEX.match(volumes_read):
        errors.append("既読冊数は0以上の整数で入力してください。")

    rating = (form.get("rating", "") or "").strip()
    if rating and not RATING_REGEX.match(rating):
        errors.append("評価は0から10の数値で入力してください。")

    return errors


def save_image(uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        return None
    original_name = secure_filename(uploaded_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    final_name = f"{timestamp}_{original_name}"
    uploaded_file.save(os.path.join(app.config["UPLOAD_FOLDER"], final_name))
    return final_name


def delete_image(file_name):
    if not file_name:
        return
    path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
    if os.path.exists(path):
        os.remove(path)


#  Routes

@app.route("/")
def index():
    db = connect_db()
    search = request.args.get("q", "").strip()
    if search:
        rows = db.execute(
            "SELECT * FROM mangas WHERE title LIKE ? OR author LIKE ? ORDER BY date_added DESC",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM mangas ORDER BY date_added DESC").fetchall()
    db.close()

    mangas = []
    for row in rows:
        manga = dict(row)
        manga["status_class"] = STATUS_CLASSES.get(manga["status"], "other")
        mangas.append(manga)

    return render_template("index.html", mangas=mangas, search=search)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        errors = validate_form(request.form)

        uploaded_file = request.files.get("image")
        if uploaded_file and uploaded_file.filename and not file_allowed(uploaded_file.filename):
            errors.append("画像はpng、jpg、jpeg、gif、webp形式のみ対応しています。")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("add.html", statuses=VALID_STATUSES, form=request.form)

        image_name = save_image(uploaded_file)

        db = connect_db()
        db.execute(
            """INSERT INTO mangas
               (title, author, genre, volumes_owned, volumes_read, status, rating, comment, image)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form.get("title", "").strip(),
                request.form.get("author", "").strip(),
                request.form.get("genre", "").strip(),
                int(request.form.get("volumes_owned") or 0),
                int(request.form.get("volumes_read") or 0),
                request.form.get("status", "").strip(),
                float(request.form["rating"]) if request.form.get("rating", "").strip() else None,
                request.form.get("comment", "").strip(),
                image_name,
            ),
        )
        db.commit()
        db.close()
        flash(f"「{request.form.get('title')}」をリストに追加しました！", "success")
        return redirect(url_for("index"))

    return render_template("add.html", statuses=VALID_STATUSES, form={})


@app.route("/edit/<int:manga_id>", methods=["GET", "POST"])
def edit(manga_id):
    db = connect_db()
    manga = db.execute("SELECT * FROM mangas WHERE id = ?", (manga_id,)).fetchone()

    if manga is None:
        db.close()
        flash("この漫画は存在しません。", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        errors = validate_form(request.form)

        uploaded_file = request.files.get("image")
        if uploaded_file and uploaded_file.filename and not file_allowed(uploaded_file.filename):
            errors.append("画像はpng、jpg、jpeg、gif、webp形式のみ対応しています。")

        if errors:
            db.close()
            for e in errors:
                flash(e, "error")
            return render_template("edit.html", manga=manga, statuses=VALID_STATUSES)

        image_name = manga["image"]
        if uploaded_file and uploaded_file.filename:
            image_name = save_image(uploaded_file)
            delete_image(manga["image"])

        db.execute(
            """UPDATE mangas SET title=?, author=?, genre=?, volumes_owned=?, volumes_read=?,
               status=?, rating=?, comment=?, image=? WHERE id=?""",
            (
                request.form.get("title", "").strip(),
                request.form.get("author", "").strip(),
                request.form.get("genre", "").strip(),
                int(request.form.get("volumes_owned") or 0),
                int(request.form.get("volumes_read") or 0),
                request.form.get("status", "").strip(),
                float(request.form["rating"]) if request.form.get("rating", "").strip() else None,
                request.form.get("comment", "").strip(),
                image_name,
                manga_id,
            ),
        )
        db.commit()
        db.close()
        flash("更新しました。", "success")
        return redirect(url_for("index"))

    db.close()
    return render_template("edit.html", manga=manga, statuses=VALID_STATUSES)


@app.route("/delete/<int:manga_id>", methods=["POST"])
def delete(manga_id):
    db = connect_db()
    manga = db.execute("SELECT * FROM mangas WHERE id = ?", (manga_id,)).fetchone()
    if manga:
        delete_image(manga["image"])
        db.execute("DELETE FROM mangas WHERE id = ?", (manga_id,))
        db.commit()
        flash(f"「{manga['title']}」を削除しました。", "success")
    db.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not db_ready():
        init_db()
    app.run(debug=True)