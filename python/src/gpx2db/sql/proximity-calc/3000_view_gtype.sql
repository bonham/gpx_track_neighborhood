-- a view which adds a type column to intersection results
drop view if exists {schema}.intersections_gtype;
create view {schema}.intersections_gtype as 
select 
	row_number() over (order by circle_id, segment_id),
	circle_id,
	segment_id,
	ST_GeometryType(wkb_geometry) as geom_type,
	wkb_geometry
from {schema}.circle_segment_intersections;