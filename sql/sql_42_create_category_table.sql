-- create table
DROP INDEX if exists track_segment_freq_categories_wkb_geometry_geom_idx;
DROP TABLE if exists public.track_segment_freq_categories;

CREATE TABLE public.track_segment_freq_categories
(
    category_segment integer not null,
    freq integer NOT NULL,
    category integer,
    wkb_geometry geometry(MultiLineString,4326),
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

-- Create strings for each segment and insert it into table

-- Dieses Art die Linestrings zu erzeugen ist nicht ganz zuverlässig. Eigentlich sollten nur Linestrings entstehen, aber ST_Linemerge schafft es in seltenen fällen nur einen MultiLineString zu erzeugen. Eigentlich sollte man nicht ST_Linemerge nutzen, sondern über die category_segment id's iterieren und mit ST_MakeLine alle vokommenden Punkte in der gegebenen Reihenfolge verketten.

insert into track_segment_freq_categories (
select
    fl.category_segment,
    fl.freq,
    null,
    ST_Multi(ST_Linemerge(ST_Collect(ST_MakeLine(tp1.wkb_geometry, tp2.wkb_geometry))))
from
	frequency_lines fl,
    track_points tp1,
    track_points tp2
where
	tp1.ogc_fid = fl.ogc_fid_start  and
    tp2.ogc_fid = fl.ogc_fid_end
group by fl.category_segment, fl.freq
order by fl.category_segment, fl.freq
);
commit;
-- insert logarithmic scale for 5 categories
update  track_segment_freq_categories
set category = round(log((select power(max(freq), 1./4) from track_segment_freq_categories), freq));
