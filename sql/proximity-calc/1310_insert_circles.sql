insert into circles (
    select
        tp.point_id,
        ST_Buffer(tp.wkb_geometry::geography, {})::geometry
    from newpoints as tp
    where tp.track_id = {}
);