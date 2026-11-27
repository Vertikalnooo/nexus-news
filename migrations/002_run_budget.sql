BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '15s';
CREATE TABLE IF NOT EXISTS nexus.run_budget (
 singleton boolean PRIMARY KEY CHECK (singleton),
 last_run timestamptz NOT NULL,
 day_utc date NOT NULL,
 runs integer NOT NULL CHECK (runs BETWEEN 1 AND 24)
);
COMMIT;
