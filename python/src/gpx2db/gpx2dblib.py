import logging
from datetime import date

logger = logging.getLogger(__name__)


class Gpx2db:

    def __init__(self, database_connection, schema):

        self.tracks_table = "{}.tracks".format(schema)
        self.tracks_id_sequence = "{}.tracks_id".format(schema)
        self.segments_table = "{}.segments".format(schema)
        self.track_points_table = "{}.track_points".format(schema)
        self.track_points_id_sequence = "{}.track_points_id".format(schema)
        self.config_table = "{}.config".format(schema)
        self.config_id_sequence = "{}.config_id".format(schema)

        self.conn = database_connection
        self.cur = self.conn.cursor()
        # if schema.upper() == 'PUBLIC':
        #     raise RuntimeError("Public schema not allowed")

        self.schema = schema

    def create_schema(self):
        "Create necessary sequences and tables"
        schema = self.schema
        logger.debug("Create schema {}".format(schema))
        cur = self.cur

        # create schema
        logger.debug("Schema variable: {}".format(schema))
        if schema != 'public':
            logger.debug("Creating schema")
            schema_sql = 'create schema {}'.format(schema)
            cur.execute(schema_sql)
            self.commit()

        logger.debug("Create schema {}".format(schema))
        self.check_create_extension()

        self.create_sequence(self.tracks_id_sequence)
        self.create_sequence(self.track_points_id_sequence)
        self.create_sequence(self.config_id_sequence)

        sql_create_tracks_table = """
            create table {}
            (
            id integer PRIMARY KEY,
            name varchar(2000),
            src varchar(2000),
            hash varchar(64),
            time timestamp with time zone,
            length double precision,
            timelength integer,
            ascent double precision,
            wkb_geometry geometry(MultiLineString,4326)
            )
        """.format(
            self.tracks_table
        )
        cur.execute(sql_create_tracks_table)
        self.commit()

        sql_create_segments_table = """
            create table {0}
            (
            track_id integer REFERENCES {1} (id),
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
            elevation double precision,
            point_time timestamp without time zone,
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

        sql_create_config_table = """
            create table {}
            (
            id integer PRIMARY KEY DEFAULT nextval('{}'::regclass),
            conftype varchar(40) not null,
            key varchar(40) not null,
            value varchar(40) not null,
            unique ( conftype, key )
            )
        """.format(
            self.config_table,
            self.config_id_sequence,
        )

        cur.execute(sql_create_config_table)
        self.commit()

    def drop_objects(self):

        tables = [
            self.segments_table,
            self.track_points_table,
            self.tracks_table,
        ]
        table_drop_commands = [
            "drop table if exists {}".format(
                i
            ) for i in tables
        ]

        sequences = [
            self.tracks_id_sequence,
            self.track_points_id_sequence
        ]
        sequence_drop_commands = [
            "drop sequence if exists {}".format(
                i
            ) for i in sequences]

        for sql in (table_drop_commands + sequence_drop_commands):
            try:
                self.cur.execute(sql)
            except Exception as e:
                logger.error(e)
            self.commit()

    def commit(self):
        self.conn.commit()

    def check_create_extension(self):
        # TODO: check if extension already there

        with self.conn.cursor() as curs:
            curs.execute(
                "SELECT extname FROM pg_extension where extname = 'postgis'")
            if (curs.rowcount == 0):

                logger.debug("Creating extension postgis in public schema")
                curs.execute(
                    "create extension "
                    "postgis"
                )
                self.commit()

    def create_sequence(self, sequence_name):

        sql = "CREATE SEQUENCE {}".format(
            sequence_name)
        self.cur.execute(sql)
        self.commit()

    def get_nextval(self, sequence):

        sql = "select nextval('{}')".format(
            sequence)
        self.cur.execute(sql)
        row = self.cur.fetchone()
        return row[0]

    def load_gpx_file(self, gpx, hash, src=None):

        track_ids_created = []
        for track in gpx.tracks:

            track_id = self.get_nextval(self.tracks_id_sequence)
            track_ids_created.append(track_id)
            self.store_track(track, track_id, hash, src)

            first_point_of_track = None

            for segnum, segment in enumerate(track.segments):

                self.store_segment(track_id, segnum)
                storelist = []

                for pointnum, point in enumerate(segment.points):

                    if first_point_of_track is None:
                        first_point_of_track = point

                    storetuple = (
                        point,
                        track_id,
                        segnum,
                        pointnum
                    )
                    storelist.append(storetuple)

                self.store_points(storelist)

            self.track_update_time(gpx, track_id, track, first_point_of_track)
            self.track_update_geometry(track_id)
            self.track_update_length(track_id)
            self.track_update_ascent(track_id)
            self.commit()
        return track_ids_created

    def store_segment(self, track_id, segment_num):
        sql = "insert into {} values ({},{})".format(
            self.segments_table,
            track_id,
            segment_num
        )
        self.cur.execute(sql)

    def extract_extensions(self, ext_list):

        r = {x.tag: x.text for x in ext_list}
        return r

    def store_track(self, track, rowid, hash, src=None):

        # we do not store length and totalascent, we calculate it later

        name = track.name

        # TODO: validate if key exists:
        ext = self.extract_extensions(track.extensions)
        time = ext.get("time", None)
        timelength = ext.get("timelength", None)

        def wrapquotes(s):
            if s is None:
                return 'NULL'
            else:
                return "'{}'".format(s)

        sql = """
            insert into {}
            (id, name, hash, src, time, timelength)
            values({},{},{},{},{},{})
        """.format(
            self.tracks_table,
            rowid,
            wrapquotes(name),
            wrapquotes(hash),
            wrapquotes(src),
            wrapquotes(time),
            wrapquotes(timelength),
        )
        self.cur.execute(sql)

    def store_points(self, storelist):

        sql = (
            "insert into {} "
            "  ("
            "       track_id, track_segment_id,"
            "       segment_point_id, elevation, point_time, wkb_geometry"
            "  )"
            "  values (%s, %s, %s, %s, %s, ST_GeomFromText('POINT(%s %s)', 4326))").format(
            self.track_points_table
        )

        for storetuple in storelist:

            (point, track_id, track_seg_id, segment_point_id) = storetuple

            elevation = point.elevation or None

            point_date = point.time or None

            self.cur.execute(sql, (track_id,
                                   track_seg_id,
                                   segment_point_id,
                                   elevation,
                                   point_date,
                                   point.longitude,
                                   point.latitude
                                   )
                             )

    def track_update_time(self, gpx, track_id, track, first_point_of_track):

        ext = self.extract_extensions(track.extensions)
        time = ext.get("time", None)

        # if time is already in gpx track extensions then good
        if time is not None:
            logger.debug(
                "Time was already in track extensions: {}".format(
                    time))
            return

        alternate_time = None
        # next look in metadata
        if hasattr(gpx, 'time') and gpx.time:
            alternate_time = gpx.time.isoformat()
            logger.debug("Retrieved time from gpx metadata: {}".format(
                alternate_time))

        # do nothing if time attribute is not in point
        elif first_point_of_track.time is None:
            logger.debug("Could not find time in any attributes")
            return

        else:
            alternate_time = first_point_of_track.time.isoformat()

        # else update table
        sql = """
            update {}.tracks
            set  time = '{}'  where id = {}
            """.format(
            self.schema,
            alternate_time,
            track_id
        )
        self.cur.execute(sql)

    def track_update_geometry(self, track_id):

        sql = """
            with base as (
                select ST_MakeLine(wkb_geometry order by id) as wkb_geometry
                from {1}.track_points where track_id = {0}
            )
            update {1}.tracks set wkb_geometry = subquery.wkb_geometry from (
                select ST_Collect(wkb_geometry) as wkb_geometry
                from base
            ) as subquery
            where id = {0}
        """.format(track_id, self.schema)

        self.cur.execute(sql)

    def track_update_length(self, track_id):

        sql = """
            update {1}.tracks
                set length = subquery.length
            from (
                select
                    id,
                    ST_Length(wkb_geometry::geography) as length
                from {1}.tracks
            ) as subquery
            where
                subquery.id = {0} and
                tracks.id = {0}
        """.format(track_id, self.schema)

        self.cur.execute(sql)

    def track_update_ascent(self, track_id):

        sql = """
            with base as (
                select
                    id,
                    track_id,
                    track_segment_id,
                    elevation - lag(elevation) over (
                        partition by
                            track_id,
                            track_segment_id
                            order by id) as diff
                from {1}.track_points
                where
                    track_points.elevation != 0
                    and track_id = {0}
                order by id
            )
            update {1}.tracks
                set ascent = subquery.ascent
            from (
                select
                    track_id,
                    sum(greatest(0, diff)) as ascent
                from base
                group by(track_id)
            ) as subquery
            where tracks.id = {0}
            and subquery.track_id = {0}
        """.format(track_id, self.schema)

        self.cur.execute(sql)
