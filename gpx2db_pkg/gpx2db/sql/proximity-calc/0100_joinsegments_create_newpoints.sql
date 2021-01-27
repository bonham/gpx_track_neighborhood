--- walk through all points, joín segments of same tracks which are not far apart
--- by inserting points into segments and renumber the segment id

insert into joined_points
with clipped_points as (
	SELECT
		*
	FROM track_points tp
	where
		{}
),
base as (
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
    			and
					(ST_Distance(tp1.wkb_geometry::geography, tp2.wkb_geometry::geography) >= 30)
        )
    	then 1 --- marker 
    	else null 
    end as marker,
    tp1.wkb_geometry
from clipped_points tp1 left join clipped_points tp2
on
    tp1.id = tp2.id + 1 -- vergleiche mit vorhergehendem punkt
where
	tp1.track_id = {}
order by id
)
select 
	id as point_id,
    track_id,
    track_segment_id_old, 
	case when marker = 1
		then nextval('joinsegments_seq')
		else currval('joinsegments_seq')
	end as segment_id,
    wkb_geometry
from base;

