INSERT INTO public.all_track_points(
	point_id, ogc_fid, track_fid, track_seg_id, track_seg_point_id, ele, "time", magvar, geoidheight, name, cmt, "desc", src, link1_href, link1_text, link1_type, link2_href, link2_text, link2_type, sym, type, fix, sat, hdop, vdop, pdop, ageofdgpsdata, dgpsid, wkb_geometry)
	SELECT 
	nextval('all_track_points_point_id_seq'), 
	tp.ogc_fid, 
	at.track_id,
    tp.track_seg_id,
    tp.track_seg_point_id,
    tp.ele,
    tp."time",
    tp.magvar,
    tp.geoidheight,
    tp.name,
    tp.cmt,
    tp."desc",
    tp.src,
    tp.link1_href,
    tp.link1_text,
    tp.link1_type,
    tp.link2_href,
    tp.link2_text,
    tp.link2_type,
    tp.sym,
    tp.type,
    tp.fix,
    tp.sat,
    tp.hdop,
    tp.vdop,
    tp.pdop,
    tp.ageofdgpsdata,
    tp.dgpsid,
    tp.wkb_geometry

	from track_points tp left join all_tracks at 
	on tp.track_fid = at.ogc_fid 
	where at.file_id = %s
	order by tp.ogc_fid;
