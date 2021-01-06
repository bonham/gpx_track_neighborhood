--- walk through all points, joín segments of same tracks which are not far apart
--- by inserting points into segments and renumber the segment id

--- new table for points
drop index if exists newpoints_seg_idx;
drop index if exists newpoints_tr_idx;
drop index if exists newpoints_geom_idx;

drop table if exists public.newpoints cascade;
create table public.newpoints
(
    ogc_fid integer not NULL,
    track_id integer not null,
    track_segment_id_old integer not null,
    segment_id integer not null,
    wkb_geometry geometry(Point,4326) not null,
    constraint newpoints_pk primary key (ogc_fid )
);
create index newpoints_seg_idx on newpoints(segment_id);
create index newpoints_tr_idx on newpoints(track_id);
CREATE INDEX newpoints_geom_idx
    ON newpoints USING gist(wkb_geometry);


--- sequences
drop sequence if exists joinsegments_seq;
create sequence joinsegments_seq;

---- insert
insert into newpoints
with base as (
select 
	tp1.id,
    tp1.track_id,
    tp1.track_segment_id as track_segment_id_old,
    case 
    	--- make a new segment marker when
    	when 
    		-- no predecessor ( first point )
    		tp2.track_id is null
    		or
    		-- new track starts
    		tp1.track_id != tp2.track_id
    		or 
    		-- new segment starts, but only when distance bigger than threshold
    		( 
                (tp1.track_segment_id != tp2.track_segment_id)
    			and (ST_Distance(tp1.wkb_geometry::geography, tp2.wkb_geometry::geography) >= 30)
            )
    	then 1 --- marker 
    	else null 
    end as marker,
    tp1.wkb_geometry
from track_points tp1 left join track_points tp2
on
    tp1.id = tp2.id + 1 -- vergleiche mit vorhergehendem punkt
order by id
)
select 
	id as ogc_fid,
    track_id,
    track_segment_id_old, 
	case when marker = 1
		then nextval('joinsegments_seq')
		else currval('joinsegments_seq')
	end as segment_id,
    wkb_geometry
from base;

-- create a view with segments before subsegments are calculated
-- just for debugging purposes
drop view if exists newpoints_segments;
create view newpoints_segments as
select
	segment_id,
	track_id,
	count(ogc_fid),
	ST_MakeLine(wkb_geometry order by ogc_fid)
from newpoints
group by track_id, segment_id
