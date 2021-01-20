insert into newsegments
select
	segment_id,
	track_id,
	count(point_id),
	ST_MakeLine(wkb_geometry order by point_id)
from newpoints
where track_id = {}
group by track_id, segment_id;