CREATE SEQUENCE track_files_seq;

CREATE TABLE track_files
(
    file_id integer NOT NULL DEFAULT nextval('track_files_seq'::regclass),
    file_name varchar(2000) not null,
    CONSTRAINT track_files_pkey PRIMARY KEY (file_id)
)
WITH (
    OIDS = FALSE
);

