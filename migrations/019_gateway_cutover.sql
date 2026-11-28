BEGIN;
REVOKE EXECUTE ON FUNCTION nexus.save_preview(text,jsonb),nexus.enqueue_preview(text,jsonb) FROM nexus_preview,nexus_write_gateway;
COMMIT;
