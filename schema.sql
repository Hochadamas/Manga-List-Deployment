DROP TABLE IF EXISTS mangas;

CREATE TABLE mangas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    volumes_owned INTEGER NOT NULL DEFAULT 0,
    volumes_read INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    rating REAL,
    comment TEXT,
    image TEXT,
    date_added TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
