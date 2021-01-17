-- identify pairs of intersections , but not do the intersection right now
-- the wkb_geometry column will be empty first
insert into circle_segment_intersections (
  circle_id,
  segment_id,
  wkb_geometry
) select
    circle_id,
    segment_id,
    ST_Intersection(ci_geom, se_geom)
  from (
    select
      ci.circle_id,
      se.segment_id,
      ci.wkb_geometry as ci_geom,
      se.wkb_geometry as se_geom
    from
      newpoints np,
      circles as ci,
      newsegments as se
    where
      np.point_id = ci.circle_id
      and
      ST_Intersects(ci.wkb_geometry, se.wkb_geometry)
      -- optional where clause 
      {0}
  ) as identified_sections