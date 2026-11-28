BEGIN;
CREATE ROLE nexus_mock_worker NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
CREATE ROLE nexus_switch_operator NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
GRANT USAGE ON SCHEMA nexus TO nexus_mock_worker,nexus_switch_operator;
GRANT SELECT,INSERT ON nexus.outbox TO nexus_mock_worker;
GRANT UPDATE(state,message_id) ON nexus.outbox TO nexus_mock_worker;
GRANT SELECT ON nexus.publication_control TO nexus_mock_worker,nexus_switch_operator;
GRANT UPDATE(enabled) ON nexus.publication_control TO nexus_switch_operator;
COMMIT;
