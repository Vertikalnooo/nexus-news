BEGIN;
CREATE TABLE nexus.gemini_policy(singleton boolean PRIMARY KEY CHECK(singleton), daily_limit integer NOT NULL CHECK(daily_limit BETWEEN 0 AND 20));
INSERT INTO nexus.gemini_policy VALUES(true,0);
CREATE TABLE nexus.gemini_usage(day_utc date PRIMARY KEY, used integer NOT NULL CHECK(used BETWEEN 1 AND 20));
REVOKE ALL ON nexus.gemini_policy,nexus.gemini_usage FROM PUBLIC,nexus_preview;
CREATE FUNCTION nexus.reserve_gemini() RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE cap integer; reserved integer;
BEGIN
 SELECT daily_limit INTO cap FROM nexus.gemini_policy WHERE singleton FOR SHARE;
 IF cap IS NULL OR cap=0 THEN RETURN false; END IF;
 INSERT INTO nexus.gemini_usage VALUES ((statement_timestamp() AT TIME ZONE 'UTC')::date,1)
 ON CONFLICT(day_utc) DO UPDATE SET used=nexus.gemini_usage.used+1 WHERE nexus.gemini_usage.used<cap
 RETURNING used INTO reserved;
 RETURN reserved IS NOT NULL;
END $$;
GRANT SELECT,UPDATE ON nexus.gemini_policy TO nexus_budget_owner;
GRANT SELECT,INSERT,UPDATE ON nexus.gemini_usage TO nexus_budget_owner;
GRANT CREATE ON SCHEMA nexus TO nexus_budget_owner;
ALTER FUNCTION nexus.reserve_gemini() OWNER TO nexus_budget_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_budget_owner;
REVOKE ALL ON FUNCTION nexus.reserve_gemini() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.reserve_gemini() TO nexus_preview;
COMMIT;
