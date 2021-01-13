drop table if exists newsegments;
create table newsegments (
	segment_id integer primary key,
	track_id integer not null,
	numpoints integer not null,
	wkb_geometry geometry(LineString,4326) not null	
);
