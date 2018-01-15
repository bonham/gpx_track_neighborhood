--- walk through all points, joín segments of same tracks which are not far apart
--- by inserting points into segments and renumber the segment id

--- new table for points
drop table if exists public.newpoints;
create table public.newpoints
(
    ogc_fid integer not NULL,
    track_fid integer not null,
    track_seg_id_old integer not null,
    segment_id integer not null,
    wkb_geometry geometry(Point,4326) not null,
    constraint newpoints_pk primary key (ogc_fid )
);
create index on newpoints(segment_id);
CREATE INDEX newpoints_geom_idx
    ON newpoints USING gist(wkb_geometry);


--- sequences
drop sequence if exists joinsegments_seq;
create sequence joinsegments_seq;

---- insert
insert into newpoints
with base as (
select 
	tp1.ogc_fid,
    tp1.track_fid,
    tp1.track_seg_id as track_seg_id_old,
    case 
    	--- make a new segment marker when
    	when 
    		-- no predecessor ( first point )
    		tp2.track_fid is null
    		or
    		-- new track starts
    		tp1.track_fid != tp2.track_fid
    		or 
    		-- new segment starts, but only when distance bigger than threshold
    		( 
                (tp1.track_seg_id != tp2.track_seg_id)
    			and (ST_Distance(tp1.wkb_geometry::geography, tp2.wkb_geometry::geography) >= 30)
            )
    	then 1 --- marker 
    	else null 
    end as marker,
    tp1.wkb_geometry
from track_points tp1 left join track_points tp2
on
    tp1.ogc_fid = tp2.ogc_fid + 1 -- vergleiche mit vorhergehendem punkt
order by ogc_fid
)
select 
	ogc_fid,
    track_fid,
    track_seg_id_old, 
	case when marker = 1
		then nextval('joinsegments_seq')
		else currval('joinsegments_seq')
	end as segment_id,
    wkb_geometry
from base;
commit;
--- new table for segments
drop table if exists public.newsegments;
create table public.newsegments
(
    segment_id integer not NULL,
    track_fid integer not null,
    wkb_geometry geometry(LineString,4326),
    constraint newsegments_pk primary key (segment_id)
);
CREATE INDEX newsegments_geom_idx
    ON newsegments USING gist(wkb_geometry);
    
--- insert into segment table
insert into newsegments
with base as (
select * from newpoints order by ogc_fid ) 
select segment_id, track_fid, ST_MakeLine(wkb_geometry)
from base
group by segment_id, track_fid


