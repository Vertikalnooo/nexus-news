BEGIN;
CREATE ROLE nexus_queue_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
GRANT USAGE ON SCHEMA nexus TO nexus_queue_owner;
GRANT SELECT ON nexus.preview_session TO nexus_queue_owner;
GRANT SELECT,INSERT ON nexus.drafts,nexus.outbox TO nexus_queue_owner;
REVOKE INSERT ON nexus.drafts,nexus.outbox FROM nexus_preview;
REVOKE INSERT ON nexus.outbox FROM nexus_mock_worker;
CREATE FUNCTION nexus.save_preview(u text,p jsonb) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE n integer;
BEGIN
 IF NOT EXISTS(SELECT 1 FROM nexus.preview_session WHERE singleton AND runs>0 AND clock_timestamp()>=starts_at AND clock_timestamp()<starts_at+interval '48 hours') THEN RETURN false; END IF;
 IF p->'preview'->>'mode' IS DISTINCT FROM 'dry-run' OR p->'preview'->'sent' IS DISTINCT FROM 'false'::jsonb THEN RETURN false; END IF;
 INSERT INTO nexus.drafts(url,payload) VALUES(u,p||'{"publication_eligible":false}'::jsonb) ON CONFLICT DO NOTHING;
 GET DIAGNOSTICS n=ROW_COUNT; RETURN n=1;
END $$;
CREATE FUNCTION nexus.enqueue_preview(k text,p jsonb) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE n integer;
BEGIN
 IF NOT EXISTS(SELECT 1 FROM nexus.preview_session WHERE singleton AND runs>0 AND clock_timestamp()>=starts_at AND clock_timestamp()<starts_at+interval '48 hours') THEN RETURN false; END IF;
 IF p->>'mode' IS DISTINCT FROM 'dry-run' OR p->'sent' IS DISTINCT FROM 'false'::jsonb THEN RETURN false; END IF;
 INSERT INTO nexus.outbox(id,payload) VALUES(k,p||'{"publication_eligible":false,"review_required":true}'::jsonb) ON CONFLICT DO NOTHING;
 GET DIAGNOSTICS n=ROW_COUNT; RETURN n=1;
END $$;
GRANT CREATE ON SCHEMA nexus TO nexus_queue_owner;
ALTER FUNCTION nexus.save_preview(text,jsonb) OWNER TO nexus_queue_owner;
ALTER FUNCTION nexus.enqueue_preview(text,jsonb) OWNER TO nexus_queue_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_queue_owner;
REVOKE ALL ON FUNCTION nexus.save_preview(text,jsonb),nexus.enqueue_preview(text,jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.save_preview(text,jsonb),nexus.enqueue_preview(text,jsonb) TO nexus_preview;
COMMIT;
