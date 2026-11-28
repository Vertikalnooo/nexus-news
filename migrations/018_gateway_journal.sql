BEGIN;
CREATE TABLE nexus.gateway_journal(request_id uuid PRIMARY KEY, fingerprint bytea NOT NULL, outcome boolean NOT NULL);
REVOKE ALL ON nexus.gateway_journal FROM PUBLIC,nexus_preview,nexus_write_gateway;
GRANT SELECT,INSERT ON nexus.gateway_journal TO nexus_queue_owner;
CREATE FUNCTION nexus.gateway_write(i uuid,op text,k text,p jsonb) RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE h bytea; old_hash bytea; result boolean;
BEGIN
 IF i IS NULL OR op IS NULL OR op NOT IN ('save','enqueue') OR k IS NULL OR length(k) NOT BETWEEN 1 AND 2048 OR jsonb_typeof(p) IS DISTINCT FROM 'object' OR octet_length(p::text)>65536 THEN RAISE EXCEPTION 'invalid request'; END IF;
 h:=sha256(convert_to(jsonb_build_array(op,k,p)::text,'UTF8'));
 PERFORM pg_advisory_xact_lock(hashtextextended(i::text,0));
 SELECT fingerprint,outcome INTO old_hash,result FROM nexus.gateway_journal WHERE request_id=i;
 IF FOUND THEN
  IF old_hash<>h THEN RAISE EXCEPTION 'request conflict' USING ERRCODE='22023'; END IF;
  RETURN result;
 END IF;
 IF op='save' THEN result:=nexus.save_preview(k,p); ELSE result:=nexus.enqueue_preview(k,p); END IF;
 INSERT INTO nexus.gateway_journal VALUES(i,h,result);
 RETURN result;
END $$;
GRANT CREATE ON SCHEMA nexus TO nexus_queue_owner;
ALTER FUNCTION nexus.gateway_write(uuid,text,text,jsonb) OWNER TO nexus_queue_owner;
REVOKE CREATE ON SCHEMA nexus FROM nexus_queue_owner;
REVOKE ALL ON FUNCTION nexus.gateway_write(uuid,text,text,jsonb) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus.gateway_write(uuid,text,text,jsonb) TO nexus_write_gateway;
COMMIT;
