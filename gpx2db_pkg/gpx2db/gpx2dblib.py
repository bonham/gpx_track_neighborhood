class Gpx2db:

    def __init__(self, database_connection):

        self.tracks_table = "tracks"
        self.tracks_id_sequence = "tracks_id"
        self.segments_table = "segments"
        self.track_points_table = "track_points"
        self.track_points_id_sequence = "track_points_id"

        self.conn = database_connection
        self.cur = self.conn.cursor()

    def init_db(self, drop=False):
        "Create necessary sequences and tables"

        self.check_create_extension()

        if drop:
            self.drop_objects()

        cur = self.cur

        self.create_sequence(self.tracks_id_sequence)
        self.create_sequence(self.track_points_id_sequence)

        sql_create_tracks_table = """
            create table {}
            (
            id integer PRIMARY KEY,
            name varchar(2000),
            src varchar(2000),
            hash varchar(64),
            wkb_geometry geometry(MultiLineString,4326)
            )
        """.format(
            self.tracks_table
        )
        cur.execute(sql_create_tracks_table)
        self.commit()

        sql_create_segments_table = """
            create table {}
            (
            track_id integer REFERENCES {} (id),
            track_segment_id integer NOT NULL,
            unique ( track_id, track_segment_id )
            )
        """.format(
            self.segments_table,
            self.tracks_table
        )
        cur.execute(sql_create_segments_table)
        self.commit()

        sql_create_points_table = """
            create table {}
            (
            id integer PRIMARY KEY DEFAULT nextval('{}'::regclass),
            track_id integer REFERENCES {} (id),
            track_segment_id integer not null,
            segment_point_id integer not null,
            wkb_geometry geometry(Point,4326),
            unique ( track_id, track_segment_id, segment_point_id )
            )
        """.format(
            self.track_points_table,
            self.track_points_id_sequence,
            self.tracks_table
        )

        cur.execute(sql_create_points_table)
        self.commit()

    def drop_objects(self):

        tables = [
            self.segments_table,
            self.track_points_table,
            self.tracks_table,
        ]
        table_drop_commands = [
            "drop table if exists {}".format(i) for i in tables]

        sequences = [
            self.tracks_id_sequence,
            self.track_points_id_sequence
        ]
        sequence_drop_commands = [
            "drop sequence if exists {}".format(i) for i in sequences]

        for sql in (table_drop_commands + sequence_drop_commands):
            try:
                self.cur.execute(sql)
            except Exception as e:
                print(e)
            self.commit()

    def commit(self):
        self.conn.commit()

    def check_create_extension(self):

        self.cur.execute(
            "SELECT extname FROM pg_extension where extname = 'postgis'")
        r = self.cur.fetchall()

        if len(r) == 0:
            self.cur.execute("create extension postgis")
            self.commit()

    def create_sequence(self, sequence_name):

        sql = "CREATE SEQUENCE {}".format(sequence_name)
        self.cur.execute(sql)
        self.commit()

    def get_nextval(self, sequence):

        sql = "select nextval('{}')".format(sequence)
        self.cur.execute(sql)
        row = self.cur.fetchone()
        return row[0]

    def load_gpx_file(self, gpx, hash, src=None):

        track_ids_created = []
        for track in gpx.tracks:

            track_id = self.get_nextval(self.tracks_id_sequence)
            track_ids_created.append(track_id)
            self.store_track(track, track_id, hash, src)

            for segnum, segment in enumerate(track.segments):

                self.store_segment(track_id, segnum)
                storelist = []
                for pointnum, point in enumerate(segment.points):

                    storetuple = (
                        point,
                        track_id,
                        segnum,
                        pointnum
                    )
                    storelist.append(storetuple)

                self.store_points(storelist)

            self.track_update_geometry(track_id)
            self.commit()
        return track_ids_created

    def store_segment(self, track_id, segment_num):
        sql = "insert into {} values ({},{})".format(
            self.segments_table,
            track_id,
            segment_num
        )
        self.cur.execute(sql)

    def store_track(self, track, rowid, hash, src=None):

        name = track.name

        sql = """
            insert into {} (id, name, hash, src)
            values({},'{}','{}','{}')
        """.format(
            self.tracks_table,
            rowid,
            name,
            hash,
            src
        )
        self.cur.execute(sql)

    def store_points(self, storelist):

        sql = (
            "insert into {} "
            "  (track_id, track_segment_id, segment_point_id, wkb_geometry) "
            "  values ").format(
            self.track_points_table
        )

        sql_value_list = []
        for storetuple in storelist:

            (point, track_id, track_seg_id, segment_point_id) = storetuple

            point_wkt = "ST_GeomFromText('POINT({} {})', 4326)".format(
                point.longitude,
                point.latitude
            )

            valuepart = "({},{},{},{})".format(
                track_id,
                track_seg_id,
                segment_point_id,
                point_wkt
            )

            sql_value_list.append(valuepart)

        sql += ",".join(sql_value_list)
        self.cur.execute(sql)

    def track_update_geometry(self, track_id):

        sql = """
            with base as (
                select ST_MakeLine(wkb_geometry order by id) as wkb_geometry
                from track_points where track_id = {0}
            )
            update tracks set wkb_geometry = subquery.wkb_geometry from (
                select ST_Collect(wkb_geometry) as wkb_geometry
                from base
            ) as subquery
            where id = {0}
        """.format(track_id)

        self.cur.execute(sql)
