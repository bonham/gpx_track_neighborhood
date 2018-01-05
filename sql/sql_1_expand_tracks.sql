DROP TABLE if exists public.tracksegments;

Drop sequence if exists public.tracksegments_id_seq;

CREATE SEQUENCE public.tracksegments_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

ALTER SEQUENCE public.tracksegments_id_seq
    OWNER TO postgres;

CREATE TABLE public.tracksegments
(
    tr_linestring_id integer NOT NULL,
    track_fid integer NOT NULL,
    wkb_geometry geometry(Linestring,4326),
    CONSTRAINT tracksegments2 PRIMARY KEY (tr_linestring_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.tracksegments
    OWNER to postgres;

drop index if exists tracksegments_wkb_geometry_geom_idx;
CREATE INDEX tracksegments_wkb_geometry_geom_idx
    ON public.tracksegments USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

insert into tracksegments (
    select 
		nextval('tracksegments_id_seq'),
    	tr.ogc_fid,
    	(ST_Dump(tr.wkb_geometry)).geom as geom
	from tracks tr
    order by tr.ogc_fid
);


