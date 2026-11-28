BEGIN;
CREATE FUNCTION nexus.preview_remaining() RETURNS double precision LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
 SELECT COALESCE((SELECT CASE WHEN clock_timestamp()>=starts_at THEN GREATEST(0,extract(epoch FROM starts_at+interval '48 hours'-clock_timestamp())) ELSE 0 END FROM nexus.preview_session WHERE singleton),0)::double precision
$$;
GRANT CREATE ON SCHEMA nexus TO nexus_budget_owner;
ALTER FUNCTION nexus.preview_remaining() OWNER TO nexus_budget_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_budget_owner;
REVOKE ALL ON FUNCTION nexus.preview_remaining() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.preview_remaining() TO nexus_preview;
COMMIT;
