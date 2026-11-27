CREATE SCHEMA IF NOT EXISTS nexus;
CREATE TABLE IF NOT EXISTS nexus.drafts (
 url text PRIMARY KEY,
 payload jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS nexus.run_budget (
 singleton boolean PRIMARY KEY CHECK (singleton),
 last_run timestamptz NOT NULL,
 day_utc date NOT NULL,
 runs integer NOT NULL CHECK (runs BETWEEN 1 AND 24)
);
