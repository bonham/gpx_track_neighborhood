drop table if exists {schema}.newsegments;
create table {schema}.newsegments (
	segment_id integer primary key,
	track_id integer not null,
	numpoints integer not null,
	wkb_geometry geometry(LineString,4326) not null	
);
