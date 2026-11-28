BEGIN;
CREATE OR REPLACE FUNCTION nexus.reserve_run() RETURNS boolean
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, pg_temp
AS $fn$
WITH reserved AS (
                INSERT INTO nexus.run_budget AS b (singleton,last_run,day_utc,runs)
                VALUES (true,statement_timestamp(),(statement_timestamp() AT TIME ZONE 'UTC')::date,1)
                ON CONFLICT (singleton) DO UPDATE SET
                    last_run=EXCLUDED.last_run,
                    day_utc=EXCLUDED.day_utc,
                    runs=CASE WHEN b.day_utc=EXCLUDED.day_utc THEN b.runs+1 ELSE 1 END
                WHERE EXCLUDED.last_run >= b.last_run + interval '1 hour'
                  AND EXCLUDED.day_utc >= b.day_utc
                  AND (b.day_utc<>EXCLUDED.day_utc OR b.runs<24)
                RETURNING runs
            )
SELECT EXISTS (SELECT 1 FROM reserved);
$fn$;
REVOKE ALL ON FUNCTION nexus.reserve_run() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.reserve_run() TO nexus_preview;
REVOKE ALL ON nexus.run_budget FROM nexus_preview;
COMMIT;
