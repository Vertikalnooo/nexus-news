BEGIN;
ALTER TABLE nexus.gemini_policy ADD COLUMN minute_limit integer NOT NULL DEFAULT 0 CHECK(minute_limit BETWEEN 0 AND 1);
CREATE TABLE nexus.gemini_last(singleton boolean PRIMARY KEY CHECK(singleton), last_at timestamptz NOT NULL);
REVOKE ALL ON nexus.gemini_last FROM PUBLIC,nexus_preview;
GRANT SELECT,INSERT,UPDATE ON nexus.gemini_last TO nexus_budget_owner;
CREATE OR REPLACE FUNCTION nexus.reserve_gemini() RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE cap integer; rpm integer; reserved integer; stamp timestamptz; previous timestamptz;
BEGIN
 SELECT daily_limit,minute_limit INTO cap,rpm FROM nexus.gemini_policy WHERE singleton FOR UPDATE;
 IF cap IS NULL OR cap=0 OR rpm=0 THEN RETURN false; END IF;
 stamp:=clock_timestamp();
 SELECT last_at INTO previous FROM nexus.gemini_last WHERE singleton;
 IF previous IS NOT NULL AND stamp<previous+interval '60 seconds' THEN RETURN false; END IF;
 INSERT INTO nexus.gemini_usage VALUES ((stamp AT TIME ZONE 'UTC')::date,1)
 ON CONFLICT(day_utc) DO UPDATE SET used=nexus.gemini_usage.used+1 WHERE nexus.gemini_usage.used<cap
 RETURNING used INTO reserved;
 IF reserved IS NULL THEN RETURN false; END IF;
 INSERT INTO nexus.gemini_last VALUES(true,stamp) ON CONFLICT(singleton) DO UPDATE SET last_at=EXCLUDED.last_at;
 RETURN true;
END $$;
COMMIT;
