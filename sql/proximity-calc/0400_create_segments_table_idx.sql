CREATE INDEX newsegments_geom_idx
    ON newsegments USING gist
    (wkb_geometry); 