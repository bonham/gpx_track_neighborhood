-- a view which splits up paths of multilinestring intersections
drop view if exists intersections_multiline_paths;
create view intersections_multiline_paths as
select 
	row_number() over (order by circle_id, segment_id, path) as ml_id,
	circle_id,
	segment_id,
	path,
	wkb_geometry
from (
	select
		circle_id,
		segment_id,
		(ST_Dump(wkb_geometry)).path[1],
		(ST_Dump(wkb_geometry)).geom as wkb_geometry
	from
		intersections_gtype
	where
		intersections_gtype.geom_type = 'ST_MultiLineString'
) as base;

-- a view which counts consecutive paths (debug view)
drop view if exists count_ml_debug;
create view count_ml_debug as
select 	
		circle_id,
		segment_id,
		lastpath,
		path,
		ST_Endpoint(lastgeom) =	ST_Startpoint(geom) as point_match,
		count(*) filter(where( not ST_Endpoint(lastgeom) = ST_Startpoint(geom))) over
			(partition by circle_id, segment_id, path order by path) + 1 as num
from (
	select 
		circle_id,
		segment_id,
		path,
		lag(path) over (partition by circle_id, segment_id order by path) as lastpath,
		geom,
		lag(geom) over (partition by circle_id, segment_id order by path) as lastgeom 

	from (
		select
			row_number,
			circle_id,
			segment_id,
			(ST_Dump(wkb_geometry)).path[1],
			(ST_Dump(wkb_geometry)).geom
		from
			intersections_gtype ig
		where
			ig.geom_type = 'ST_MultiLineString'
		order by
			row_number
	) as multilinestrings
) as ml_paths
order by
	circle_id,
	segment_id,
	path