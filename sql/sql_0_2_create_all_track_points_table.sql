CREATE SEQUENCE all_track_points_point_id_seq;

CREATE TABLE all_track_points
(
    point_id integer NOT NULL DEFAULT nextval('all_track_points_point_id_seq'::regclass),
    ogc_fid integer NOT NULL,
    track_fid integer,
    track_seg_id integer,
    track_seg_point_id integer,
    ele double precision,
    "time" timestamp with time zone,
    magvar double precision,
    geoidheight double precision,
    name character varying COLLATE pg_catalog."default",
    cmt character varying COLLATE pg_catalog."default",
    "desc" character varying COLLATE pg_catalog."default",
    src character varying COLLATE pg_catalog."default",
    link1_href character varying COLLATE pg_catalog."default",
    link1_text character varying COLLATE pg_catalog."default",
    link1_type character varying COLLATE pg_catalog."default",
    link2_href character varying COLLATE pg_catalog."default",
    link2_text character varying COLLATE pg_catalog."default",
    link2_type character varying COLLATE pg_catalog."default",
    sym character varying COLLATE pg_catalog."default",
    type character varying COLLATE pg_catalog."default",
    fix character varying COLLATE pg_catalog."default",
    sat integer,
    hdop double precision,
    vdop double precision,
    pdop double precision,
    ageofdgpsdata double precision,
    dgpsid integer,
    wkb_geometry geometry(Point,4326),
    CONSTRAINT all_track_points_pkey PRIMARY KEY (point_id),
    foreign key (track_fid) references all_tracks (track_id)
)
WITH (
    OIDS = FALSE
);

create unique index all_track_points_uniq on all_track_points(ogc_fid, track_fid);

CREATE INDEX all_track_points_wkb_geometry_geom_idx
    ON all_track_points USING gist
    (wkb_geometry);
