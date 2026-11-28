BEGIN;
ALTER TABLE nexus.outbox ADD COLUMN claim_hash bytea, ADD COLUMN claim_until timestamptz;
GRANT SELECT(claim_hash,claim_until),UPDATE(claim_hash,claim_until) ON nexus.outbox TO nexus_queue_owner;
REVOKE EXECUTE ON FUNCTION nexus.claim_mock(text),nexus.finish_mock(text,text) FROM nexus_mock_worker;
CREATE FUNCTION nexus.claim_mock(k text,h bytea) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE p jsonb;
BEGIN
 IF NOT nexus.lock_publication_switch() OR h IS NULL OR octet_length(h)<>32 THEN RETURN NULL; END IF;
 UPDATE nexus.outbox SET state='unknown',claim_hash=h,claim_until=clock_timestamp()+interval '60 seconds' WHERE id=k AND state='pending' RETURNING payload INTO p;
 RETURN p;
END $$;
CREATE FUNCTION nexus.finish_mock(k text,t bytea,m text) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 IF NOT nexus.lock_publication_switch() OR t IS NULL OR octet_length(t)<>32 OR m IS NULL OR m !~ '^mock-[0-9]+$' THEN RETURN false; END IF;
 UPDATE nexus.outbox SET state='simulated',message_id=m,claim_hash=NULL,claim_until=NULL WHERE id=k AND state='unknown' AND claim_hash=sha256(t) AND clock_timestamp()<claim_until;
 RETURN FOUND;
END $$;
GRANT CREATE ON SCHEMA nexus TO nexus_queue_owner;
ALTER FUNCTION nexus.claim_mock(text,bytea) OWNER TO nexus_queue_owner;
ALTER FUNCTION nexus.finish_mock(text,bytea,text) OWNER TO nexus_queue_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_queue_owner;
REVOKE ALL ON FUNCTION nexus.claim_mock(text,bytea),nexus.finish_mock(text,bytea,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.claim_mock(text,bytea),nexus.finish_mock(text,bytea,text) TO nexus_mock_worker;
DROP FUNCTION nexus.claim_mock(text);
DROP FUNCTION nexus.finish_mock(text,text);
COMMIT;
