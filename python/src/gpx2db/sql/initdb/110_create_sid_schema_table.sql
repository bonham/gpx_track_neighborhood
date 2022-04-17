-- Table: tm_meta.schema_sid

-- DROP TABLE IF EXISTS tm_meta.schema_sid;

CREATE TABLE IF NOT EXISTS tm_meta.schema_sid
(
    sid character varying(10) NOT NULL,
    schema character varying(30) NOT NULL,
    CONSTRAINT schema_sid_pk PRIMARY KEY (sid, schema)
);
