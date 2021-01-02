class SetupDb:

    def __init__(self, database_connection):

        self.tracks_table = "tracks"
        self.tracks_id_sequence = "tracks_id"
        self.track_points_table = "track_points"
        self.track_points_id_sequence = "track_points_id"

        self.conn = database_connection
        self.cur = self.conn.cursor()

    def drop_objects(self):

        sequences = [
            self.tracks_id_sequence,
            self.track_points_id_sequence
        ]
        sequence_drop_commands = [
            "drop sequence {}".format(i) for i in sequences]

        tables = [
            self.tracks_table,
            self.track_points_table
        ]
        table_drop_commands = ["drop table {}".format(i) for i in tables]

        for sql in (sequence_drop_commands + table_drop_commands):
            try:
                self.cur.execute(sql)
            except Exception as e:
                print(e)

    def commit(self):
        self.conn.commit()

    def init_db(self, drop=False):
        "Create necessary sequences and tables"

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
            wkb_geometry geometry(MultiLineString,4326)
            )
        """.format(
            self.tracks_table
        )
        cur.execute(sql_create_tracks_table)

        sql_create_points_table = """
            create table {}
            (
            id integer PRIMARY KEY,
            track_id integer not null,
            track_segment_id integer not null,
            wkb_geometry geometry(Point,4326),
            unique ( track_id, track_segment_id )
            )
        """.format(
            self.track_points_table
        )

        cur.execute(sql_create_points_table)

    def create_sequence(self, sequence_name):

        sql = "CREATE SEQUENCE {}".format(sequence_name)
        self.cur.execute(sql)

    def get_nextval(self, sequence):

        sql = "select nextval({})".format(sequence)
        self.cur.execute(sql)
        row = self.cur.fetchone()
        return row[0]

    def load_gpx_file(self, gpx, src=None):

        for track in gpx.tracks:

            track_id = self.get_nextval(self.tracks_id_sequence)
            self.store_track(track, track_id, src)

            for segnum, segment in enumerate(track.segments):
                print("Segment: {}".format(segnum))

                for point in segment.points:
                    point_id = self.get_nextval(self.track_points_id_sequence)
                    self.store_point(
                        point,
                        point_id,
                        track_id,
                        segnum
                    )

        print("Committing ...")
        self.commit()

    def store_track(self, track, rowid, src=None):

        name = track.name

        sql = """
            insert into {} (id, name, src)
            values({},{},{}
        """.format(
            self.tracks_table,
            rowid,
            name,
            src
        )
        self.cur.execute(sql)

    def store_point(self, point, rowid, track_id, track_seg_id):

        point_wkt = "ST_GeomFromText('POINT({} {})', 4326)".format(
            point.longitude,
            point.latitude
        )

        sql_template = """
            insert into {} (id, track_id, track_segment_id, wkb_geometry)
            values({},{},{},{})
        """.format(
            rowid,
            track_id,
            track_seg_id,
            point_wkt
        )
