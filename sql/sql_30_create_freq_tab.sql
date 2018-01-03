DROP TABLE if exists public.frequency;

CREATE TABLE public.frequency
(
    ogc_fid integer NOT NULL,
    track_fid integer NOT NULL,
    freq integer NOT NULL,
    wkb_geometry geometry(Point,4326),
    CONSTRAINT frequency2 PRIMARY KEY (ogc_fid)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.frequency
    OWNER to postgres;

drop index if exists frequency_wkb_geometry_geom_idx;
CREATE INDEX frequency_wkb_geometry_geom_idx
    ON public.frequency USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

