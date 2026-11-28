BEGIN;
REVOKE UPDATE(state,message_id) ON nexus.outbox FROM nexus_mock_worker;
GRANT UPDATE(state,message_id) ON nexus.outbox TO nexus_queue_owner;
GRANT EXECUTE ON FUNCTION nexus.lock_publication_switch() TO nexus_queue_owner;
CREATE FUNCTION nexus.claim_mock(k text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE p jsonb;
BEGIN
 IF NOT nexus.lock_publication_switch() THEN RETURN NULL; END IF;
 UPDATE nexus.outbox SET state='unknown' WHERE id=k AND state='pending' RETURNING payload INTO p;
 RETURN p;
END $$;
CREATE FUNCTION nexus.finish_mock(k text,m text) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 IF NOT nexus.lock_publication_switch() OR m IS NULL OR m !~ '^mock-[0-9]+$' THEN RETURN false; END IF;
 UPDATE nexus.outbox SET state='simulated',message_id=m WHERE id=k AND state='unknown';
 RETURN FOUND;
END $$;
GRANT CREATE ON SCHEMA nexus TO nexus_queue_owner;
ALTER FUNCTION nexus.claim_mock(text) OWNER TO nexus_queue_owner;
ALTER FUNCTION nexus.finish_mock(text,text) OWNER TO nexus_queue_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_queue_owner;
REVOKE ALL ON FUNCTION nexus.claim_mock(text),nexus.finish_mock(text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.claim_mock(text),nexus.finish_mock(text,text) TO nexus_mock_worker;
COMMIT;
