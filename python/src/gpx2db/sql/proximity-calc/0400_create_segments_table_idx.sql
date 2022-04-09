CREATE INDEX newsegments_geom_idx
    ON {schema}.newsegments USING gist
    (wkb_geometry); 