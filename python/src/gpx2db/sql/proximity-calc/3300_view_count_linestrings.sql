drop view if exists count_ls;
create view count_ls as
select
	circle_id,
	count(*) as num
from
	intersections_gtype
where
	geom_type = 'ST_LineString'
group by
	circle_id