CREATE SEQUENCE all_tracks_track_id_seq;

CREATE TABLE all_tracks
(
    track_id integer not null,
    file_id integer not null,
    ogc_fid integer NOT NULL,
    name character varying COLLATE pg_catalog."default",
    wkb_geometry geometry(MultiLineString,4326),
    CONSTRAINT all_tracks_pkey PRIMARY KEY (track_id),
    foreign key (file_id) references track_files(file_id)
)
WITH (
    OIDS = FALSE
);

create unique index all_tracks_uniq on all_tracks (file_id, ogc_fid);

CREATE INDEX all_tracks_wkb_geometry_geom_idx
    ON all_tracks USING gist
    (wkb_geometry);
