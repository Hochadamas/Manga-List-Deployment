#!/bin/sh
set -e

# app.py only calls init_db() inside `if __name__ == "__main__"`, which never
# runs under gunicorn (it imports app:app directly). Initialize the SQLite
# schema here instead, once, before starting the real server.
python -c "from app import db_ready, init_db; init_db() if not db_ready() else None"

exec "$@"
