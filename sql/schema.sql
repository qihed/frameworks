-- ==========================================
-- Сервис учёта комиксов: структура базы данных
-- ==========================================

-- Серии комиксов, доступные для учёта.
CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    author TEXT NOT NULL,
    issues_total INTEGER NOT NULL,
    age_limit INTEGER NOT NULL
);

-- Пользователи сервиса.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    email TEXT NOT NULL
);

-- Записи коллекции: какую серию какой пользователь читает.
-- status_code: 1 - запланировано, 2 - читаю, 3 - прочитано, 4 - брошено.
-- is_removed: 0 - запись активна, 1 - удалена из коллекции.
CREATE TABLE IF NOT EXISTS collection_entries (
    id INTEGER PRIMARY KEY,
    series_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status_code INTEGER NOT NULL DEFAULT 1,
    issues_read INTEGER NOT NULL DEFAULT 0,
    is_removed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (series_id) REFERENCES series(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
