BEGIN;
CREATE TABLE nexus.publication_control (singleton boolean PRIMARY KEY CHECK(singleton), enabled boolean NOT NULL DEFAULT false);
INSERT INTO nexus.publication_control VALUES(true,false);
CREATE TABLE nexus.outbox (id text PRIMARY KEY, payload jsonb NOT NULL, state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','unknown','simulated')), message_id text);
REVOKE ALL ON nexus.publication_control,nexus.outbox FROM PUBLIC;
COMMIT;
