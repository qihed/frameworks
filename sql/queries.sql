-- ==========================================
-- Сервис учёта комиксов: SQL-запросы проекта
-- Проверка: sqlite3 data/comics.sqlite
-- Знак ? — параметр, значение передаётся отдельно.
-- ==========================================


-- ------------------------------------------
-- 1. Выборка списков
-- ------------------------------------------

-- 1.1. Список всех серий (страница «Серии»)
SELECT
    id,
    title,
    publisher,
    author,
    issues_total,
    age_limit
FROM series
ORDER BY title;

-- 1.2. Список пользователей
SELECT
    id,
    name,
    age,
    email
FROM users
ORDER BY name;

-- 1.3. Три самые длинные серии (ORDER BY + LIMIT)
SELECT
    id,
    title,
    issues_total
FROM series
ORDER BY issues_total DESC, title
LIMIT 3;


-- ------------------------------------------
-- 2. Фильтрация (WHERE)
-- ------------------------------------------

-- 2.1. Серии, доступные по возрасту
-- Параметр 1: возраст пользователя
SELECT
    id,
    title,
    age_limit
FROM series
WHERE age_limit <= ?
ORDER BY age_limit, title;

-- 2.2. Активные записи коллекции (удалённые не учитываются)
SELECT
    id,
    series_id,
    user_id,
    status_code,
    issues_read
FROM collection_entries
WHERE is_removed = 0
ORDER BY id;

-- 2.3. Что пользователь читает сейчас (несколько условий)
-- Параметр 1: идентификатор пользователя
SELECT
    id,
    series_id,
    issues_read
FROM collection_entries
WHERE user_id = ?
  AND status_code = 2
  AND is_removed = 0
ORDER BY id;

-- 2.4. Серии, доступные пользователю для добавления в коллекцию:
-- подходят по возрасту и ещё не добавлены им (подзапрос NOT IN)
-- Параметры: 1 и 2 — идентификатор пользователя
SELECT
    series.id,
    series.title,
    series.publisher,
    series.issues_total,
    series.age_limit
FROM series
WHERE series.age_limit <= (
        SELECT users.age
        FROM users
        WHERE users.id = ?
    )
  AND series.id NOT IN (
        SELECT collection_entries.series_id
        FROM collection_entries
        WHERE collection_entries.user_id = ?
          AND collection_entries.is_removed = 0
    )
ORDER BY series.title;


-- ------------------------------------------
-- 3. Соединение таблиц (JOIN)
-- ------------------------------------------

-- 3.1. Активные записи коллекции с названием серии и именем
-- пользователя (страница «Коллекция»)
SELECT
    collection_entries.id,
    collection_entries.status_code,
    collection_entries.issues_read,
    collection_entries.is_removed,
    series.title AS series_title,
    series.issues_total,
    users.name AS user_name
FROM collection_entries
JOIN series
    ON collection_entries.series_id = series.id
JOIN users
    ON collection_entries.user_id = users.id
WHERE collection_entries.is_removed = 0
ORDER BY users.name, series.title;

-- 3.2. Полная информация об одной записи коллекции (в том числе
-- удалённой): прогресс в процентах и число непрочитанных выпусков
-- Параметр 1: идентификатор записи
SELECT
    collection_entries.id,
    collection_entries.status_code,
    collection_entries.issues_read,
    collection_entries.is_removed,
    series.id AS series_id,
    series.title AS series_title,
    series.issues_total,
    users.name AS user_name,
    ROUND(
        collection_entries.issues_read * 100.0 / series.issues_total,
        1
    ) AS progress,
    MAX(series.issues_total - collection_entries.issues_read, 0)
        AS issues_left
FROM collection_entries
JOIN series
    ON collection_entries.series_id = series.id
JOIN users
    ON collection_entries.user_id = users.id
WHERE collection_entries.id = ?;

-- 3.3. Серии конкретного пользователя с прогрессом чтения
-- Параметр 1: идентификатор пользователя
SELECT
    series.title,
    collection_entries.issues_read,
    series.issues_total
FROM collection_entries
JOIN series
    ON collection_entries.series_id = series.id
WHERE collection_entries.user_id = ?
  AND collection_entries.is_removed = 0
ORDER BY series.title;


-- ------------------------------------------
-- 4. Агрегатные функции
-- ------------------------------------------

-- 4.1. Количество активных записей коллекции
SELECT
    COUNT(*) AS entries_count
FROM collection_entries
WHERE is_removed = 0;

-- 4.2. Сводка по сериям: количество, сумма, среднее, минимум, максимум
SELECT
    COUNT(*) AS series_count,
    SUM(issues_total) AS issues_sum,
    ROUND(AVG(issues_total), 1) AS issues_avg,
    MIN(issues_total) AS issues_min,
    MAX(issues_total) AS issues_max
FROM series;

-- 4.3. Сколько выпусков прочитано всеми пользователями
SELECT
    SUM(issues_read) AS issues_read_total
FROM collection_entries
WHERE is_removed = 0;


-- ------------------------------------------
-- 5. Группировка (GROUP BY, HAVING)
-- ------------------------------------------

-- 5.1. Количество активных записей по каждой серии. LEFT JOIN
-- сохраняет серии, которых нет ни в одной коллекции (счётчик 0)
SELECT
    series.title AS series_title,
    COUNT(collection_entries.id) AS entries_count
FROM series
LEFT JOIN collection_entries
    ON series.id = collection_entries.series_id
   AND collection_entries.is_removed = 0
GROUP BY series.id, series.title
ORDER BY entries_count DESC, series.title;

-- 5.2. Распределение активных записей по статусам чтения
SELECT
    status_code,
    CASE status_code
        WHEN 1 THEN 'запланировано'
        WHEN 2 THEN 'читаю'
        WHEN 3 THEN 'прочитано'
        WHEN 4 THEN 'брошено'
        ELSE 'не определено'
    END AS status_name,
    COUNT(*) AS entries_count
FROM collection_entries
WHERE is_removed = 0
GROUP BY status_code
ORDER BY status_code;

-- 5.3. Сводка по пользователям: записей и прочитанных выпусков
SELECT
    users.name AS user_name,
    COUNT(collection_entries.id) AS entries_count,
    COALESCE(SUM(collection_entries.issues_read), 0) AS issues_read_total
FROM users
LEFT JOIN collection_entries
    ON users.id = collection_entries.user_id
   AND collection_entries.is_removed = 0
GROUP BY users.id, users.name
ORDER BY issues_read_total DESC, users.name;

-- 5.4. Пользователи, прочитавшие больше заданного числа выпусков
-- (HAVING фильтрует группы после группировки)
-- Параметр 1: порог по числу прочитанных выпусков
SELECT
    users.name AS user_name,
    SUM(collection_entries.issues_read) AS issues_read_total
FROM users
JOIN collection_entries
    ON users.id = collection_entries.user_id
WHERE collection_entries.is_removed = 0
GROUP BY users.id, users.name
HAVING SUM(collection_entries.issues_read) > ?
ORDER BY issues_read_total DESC;


-- ------------------------------------------
-- 6. Выборка одной записи по идентификатору
-- ------------------------------------------

-- 6.1. Карточка серии
-- Параметр 1: идентификатор серии
SELECT
    id,
    title,
    publisher,
    author,
    issues_total,
    age_limit
FROM series
WHERE id = ?;

-- 6.2. Сколько пользователей держат серию в активной коллекции
-- Параметр 1: идентификатор серии
SELECT
    COUNT(*) AS entries_count
FROM collection_entries
WHERE series_id = ?
  AND is_removed = 0;
