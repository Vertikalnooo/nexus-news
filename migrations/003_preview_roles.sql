BEGIN;
SET LOCAL lock_timeout='5s';
CREATE UNIQUE INDEX IF NOT EXISTS draft_title_key ON nexus.drafts ((payload->>'title_key'));
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='nexus_preview') THEN
 CREATE ROLE nexus_preview NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
 END IF;
END $$;
REVOKE ALL ON SCHEMA nexus FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA nexus FROM PUBLIC;
GRANT USAGE ON SCHEMA nexus TO nexus_preview;
GRANT SELECT, INSERT ON nexus.drafts TO nexus_preview;
-- Budget access requires a separate hardened function before runtime login is provisioned.
COMMIT;
