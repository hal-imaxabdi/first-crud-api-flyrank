-- Runs automatically the FIRST time the Postgres container starts with an
-- empty data volume (Postgres's docker-entrypoint-initdb.d mechanism).
-- It will NOT run again on later restarts, so it's safe to keep as-is.

CREATE TABLE IF NOT EXISTS tasks (
    id    SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, done)
SELECT * FROM (VALUES
    ('Buy groceries', FALSE),
    ('Finish assignment', FALSE),
    ('Read a chapter', TRUE)
) AS seed(title, done)
WHERE NOT EXISTS (SELECT 1 FROM tasks);
