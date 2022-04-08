drop view if exists {schema}.count_ls;
create view {schema}.count_ls as
select
	circle_id,
	count(*) as num
from
	{schema}.intersections_gtype
where
	geom_type = 'ST_LineString'
group by
	circle_id