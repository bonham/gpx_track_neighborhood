DROP TABLE if exists circles;

CREATE TABLE circles
(
    circle_id integer NOT NULL,
    wkb_geometry geometry(Polygon,4326),
    CONSTRAINT circles2 PRIMARY KEY (circle_id)
);

CREATE INDEX circles_wkb_geometry_geom_idx
    ON public.circles USING gist (wkb_geometry)
    TABLESPACE pg_default;
