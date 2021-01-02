class SetupDb:

    def __init__(self, database_connection):

        self.tracks_table = "tracks"
        self.tracks_id_sequence = "tracks_id"
        self.track_points_table = "track_points"
        self.track_points_id_sequence = "track_points_id"
        self.track_segments_id_sequence = "track_segments_id"

        self.conn = database_connection
        self.cur = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def init_db(self):
        "Create necessary sequences and tables"
        cur = self.cur

        self.create_sequence(self.tracks_id_sequence)
        self.create_sequence(self.track_points_id_sequence)
        self.create_sequence(self.track_segments_id_sequence)

        sql_create_tracks_table = """
            create table {}
            (
            id integer PRIMARY KEY,
            src_file varchar(1000),
            description varchar(2000),
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

    def load_gpx_file(self, gpxpy_obj):
        pass
