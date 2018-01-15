DROP TABLE if exists public.circles;

CREATE TABLE public.circles
(
    ogc_fid integer NOT NULL,
    wkb_geometry geometry(Polygon,4326),
    CONSTRAINT circles2 PRIMARY KEY (ogc_fid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.circles
    OWNER to postgres;

drop index if exists circles_wkb_geometry_geom_idx;

insert into circles (select ogc_fid, ST_Buffer(tp.wkb_geometry::geography, {})::geometry from newpoints as tp);

CREATE INDEX circles_wkb_geometry_geom_idx
    ON public.circles USING gist
    (wkb_geometry)
    TABLESPACE pg_default;


