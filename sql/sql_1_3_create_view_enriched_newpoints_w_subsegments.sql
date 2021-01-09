drop view if exists  enriched_newpoints_w_subsegments;
create view enriched_newpoints_w_subsegments as

-- Before making linestrings we need to duplicate all points which are
-- at the edge between two segments, so that we have no gaps 
-- before splitting the segments into subsegments
-- subquery 'enriched_newpoints is representing this
with enriched_newpoints as (
	select * from (
		select 
			track_id,
			segment_id,
			subseg as orig_subseg,
			-- subseg will be changed to subseg of 'last' subseg group
			-- this is how we add the first point of next subseg as the 
			-- final point of the previous subseg
			lag(subseg) over (partition by segment_id order by segment_id, subseg) as subseg,
			ogc_fid,
			wkb_geometry
		from (
			-- selects line with lowest ogc_fid in given segment_id, subseg
			SELECT DISTINCT ON (segment_id, subseg)
				track_id,
				segment_id,
				subseg,
				ogc_fid,
				wkb_geometry
			FROM   newpoints_w_subsegments
			where subseg is not null -- for subsegs with only one point 
			-- next line is important how 'first row of next subsegment is determined'
			ORDER  BY segment_id, subseg, ogc_fid
		) as sub1
		UNION ALL
		select
			track_id,
			segment_id,
			subseg as orig_subseg,
			subseg,
			ogc_fid,
			wkb_geometry
		from newpoints_w_subsegments
		where subseg is not null -- for subsegs with only one point 
	) as uniontab
	-- next is important for the order of the points fed into ST_MakeLine
	-- hopefully we have no double ogc_fid in each subsegment
	order by segment_id, subseg, ogc_fid
)
select * from enriched_newpoints
-- the first point in first subseg of a segment does not need to be duplicated
-- and needs to be eliminated. It is marked with null value in subseg, because lag() did return null.
where subseg is not null
order by ogc_fid, subseg nulls first
