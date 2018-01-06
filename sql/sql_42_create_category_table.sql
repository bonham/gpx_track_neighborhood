-- create table
DROP TABLE if exists public.track_segment_freq_categories;

CREATE TABLE public.track_segment_freq_categories
(
    category_segment integer not null,
    freq integer NOT NULL,
    wkb_geometry geometry(Linestring,4326),
    CONSTRAINT track_segment_freq_categories_pk PRIMARY KEY (category_segment)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.track_segment_freq_categories
    OWNER to postgres;

CREATE INDEX track_segment_freq_categories_wkb_geometry_geom_idx
    ON public.track_segment_freq_categories USING gist
    (wkb_geometry)
    TABLESPACE pg_default;

create index track_segment_freq_categories_catseg on track_segment_freq_categories(freq);

-- Create linestrings for each segment and insert it into table

insert into track_segment_freq_categories (
select
    fl.category_segment,
    fl.freq,
    ST_Linemerge(ST_Collect(ST_MakeLine(tp1.wkb_geometry, tp2.wkb_geometry)))
from
	frequency_lines fl,
    track_points tp1,
    track_points tp2
where
	tp1.ogc_fid = fl.ogc_fid_start  and
    tp2.ogc_fid = fl.ogc_fid_end
group by fl.category_segment, fl.freq
order by fl.category_segment, fl.freq
)
