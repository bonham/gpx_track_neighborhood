-- create table
DROP INDEX if exists track_segment_freq_categories_wkb_geometry_geom_idx;
DROP TABLE if exists track_segment_freq_categories;

CREATE TABLE {schema}.track_segment_freq_categories
(
    category_segment integer primary key,
    freq integer NOT NULL,
    category integer,
    wkb_geometry geometry(MultiLineString,4326)
);

CREATE INDEX track_segment_freq_categories_wkb_geometry_geom_idx
    ON {schema}.track_segment_freq_categories USING gist (wkb_geometry);
create index track_segment_freq_categories_catseg
    on {schema}.track_segment_freq_categories(freq);

-- Create strings for each segment and insert it into table

-- Dieses Art die Linestrings zu erzeugen ist nicht ganz zuverlässig. Eigentlich sollten nur Linestrings entstehen, aber ST_Linemerge schafft es in seltenen fällen nur einen MultiLineString zu erzeugen. Eigentlich sollte man nicht ST_Linemerge nutzen, sondern über die category_segment id's iterieren und mit ST_MakeLine alle vokommenden Punkte in der gegebenen Reihenfolge verketten.

insert into {schema}.track_segment_freq_categories (
select
    fl.category_segment,
    fl.freq,
    null,
    ST_Multi(ST_Linemerge(ST_Collect(ST_MakeLine(np1.wkb_geometry, np2.wkb_geometry))))
from
	{schema}.frequency_lines fl,
    {schema}.newpoints np1,
    {schema}.newpoints np2
where
	np1.point_id = fl.point_id_start  and
    np2.point_id = fl.point_id_end
group by fl.category_segment, fl.freq
order by fl.category_segment, fl.freq
);
commit;
-- insert logarithmic scale for 5 categories
update  {schema}.track_segment_freq_categories
set category = round(log((select power(max(freq), 1./4) from {schema}.track_segment_freq_categories), freq));
