BEGIN;
CREATE FUNCTION nexus.guard_preview_commit() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM nexus.preview_session WHERE singleton AND runs>0 AND clock_timestamp()>=starts_at AND clock_timestamp()<starts_at+interval '48 hours') THEN
 RAISE EXCEPTION 'preview session expired' USING ERRCODE='23514';
 END IF;
 RETURN NEW;
END $$;
GRANT CREATE ON SCHEMA nexus TO nexus_queue_owner;
ALTER FUNCTION nexus.guard_preview_commit() OWNER TO nexus_queue_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_queue_owner;
REVOKE ALL ON FUNCTION nexus.guard_preview_commit() FROM PUBLIC;
CREATE CONSTRAINT TRIGGER draft_commit_guard AFTER INSERT ON nexus.drafts DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION nexus.guard_preview_commit();
CREATE CONSTRAINT TRIGGER outbox_commit_guard AFTER INSERT ON nexus.outbox DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION nexus.guard_preview_commit();
COMMIT;
