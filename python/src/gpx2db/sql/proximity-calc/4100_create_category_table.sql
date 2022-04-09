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

