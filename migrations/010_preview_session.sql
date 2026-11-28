BEGIN;
CREATE TABLE nexus.preview_session(singleton boolean PRIMARY KEY CHECK(singleton), starts_at timestamptz NOT NULL, runs integer NOT NULL DEFAULT 0 CHECK(runs BETWEEN 0 AND 48), last_run timestamptz);
REVOKE ALL ON nexus.preview_session FROM PUBLIC,nexus_preview;
GRANT SELECT,UPDATE(runs,last_run) ON nexus.preview_session TO nexus_budget_owner;
CREATE FUNCTION nexus.reserve_preview_session() RETURNS boolean LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
WITH reserved AS (
 UPDATE nexus.preview_session SET runs=runs+1,last_run=statement_timestamp()
 WHERE singleton AND statement_timestamp()>=starts_at AND statement_timestamp()<starts_at+interval '48 hours'
 AND runs<48 AND (last_run IS NULL OR statement_timestamp()>=last_run+interval '1 hour')
 RETURNING runs
) SELECT EXISTS(SELECT 1 FROM reserved)
$$;
GRANT CREATE ON SCHEMA nexus TO nexus_budget_owner;
ALTER FUNCTION nexus.reserve_preview_session() OWNER TO nexus_budget_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_budget_owner;
REVOKE ALL ON FUNCTION nexus.reserve_preview_session() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.reserve_preview_session() TO nexus_preview;
COMMIT;
