insert into newsegments
select
	segment_id,
	track_id,
	count(ogc_fid),
	ST_MakeLine(wkb_geometry order by ogc_fid)
from newpoints
group by track_id, segment_id;