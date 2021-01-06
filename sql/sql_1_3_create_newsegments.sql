--- new table for segments
drop table if exists public.newsegments;
create table public.newsegments
(
    subseg_id integer not NULL,
    segment_id integer not NULL,
    subseg integer not NULL,
    track_id integer not null,
    numpoints integer not null,
    wkb_geometry geometry(LineString,4326),
    constraint newsegments_pk primary key (subseg_id)
);

insert into newsegments
select 
  row_number() over (order by segment_id, subseg) as subseg_id,
  segment_id,
  subseg,
  track_id,
  count(ogc_fid) as numpoints,
  ST_MakeLine(wkb_geometry order by segment_id, subseg) as wkb_geometry
from newpoints_w_subsegments
where subseg is not null
group by segment_id, subseg, track_id
;

CREATE INDEX newsegments_geom_idx
    ON newsegments USING gist(wkb_geometry);
