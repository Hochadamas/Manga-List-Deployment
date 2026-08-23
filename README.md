# Manga-list

自分の漫画コレクションを簡単に管理できるWebアプリ。
A clean web app to track and manage your personal manga collection.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)

---

### Features / 機能
- **CRUD Operations**: Full management of your collection (Add, Edit, Delete).
- **Search & Filter**: Fast keyword search by title or author.
- **Image Management**: Cover upload with automatic server file deletion on removal.
- **Server-Side Validation**: Robust Python data validation using Regex.

---

### Tech Stack
- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Jinja2

---

### Quick Start

```bash
# Clone repository
git clone <https://github.com/Hochadamas/Manga-List.git>
cd Manga-list

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies & run
pip install -r requirements.txt
python app.py