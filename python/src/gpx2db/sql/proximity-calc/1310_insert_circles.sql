insert into {schema}.circles (
    select
        tp.point_id,
        ST_Buffer(tp.wkb_geometry::geography, {})::geometry
    from {schema}.newpoints as tp
    where tp.track_id = {}
);