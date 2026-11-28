BEGIN;
CREATE ROLE nexus_write_gateway NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
GRANT USAGE ON SCHEMA nexus TO nexus_write_gateway;
GRANT EXECUTE ON FUNCTION nexus.save_preview(text,jsonb),nexus.enqueue_preview(text,jsonb) TO nexus_write_gateway;
-- Runtime cutover deliberately deferred until gateway integration is verified.
COMMIT;
