-- a view which adds a type column to intersection results
drop view if exists intersections_gtype;
create view intersections_gtype as 
select 
	row_number() over (order by circle_id, segment_id),
	circle_id,
	segment_id,
	ST_GeometryType(wkb_geometry) as geom_type,
	wkb_geometry
from circle_segment_intersections;