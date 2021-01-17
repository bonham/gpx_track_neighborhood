drop view if exists count_ml_consecutive;
create view count_ml_consecutive as
select 	
		circle_id,
		count(*) filter(where( not ST_Endpoint(lastgeom) = ST_Startpoint(geom)))  + 1 as num
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
group by
	circle_id
	