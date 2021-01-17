import os
import psycopg2 as pg2
import gpxpy
from .gpx2dblib import Gpx2db

PG_ADMIN_DB = "postgres"
PG_ADMIN_DB_USER = "postgres"


def gpximport(
        filelist, database_name, delete_mode,
        host, db_user, password, dbport):

    # connect to newly created db
    conn = pg2.connect(
        "dbname={} host={} user={} password={} port={}".format(
            database_name,
            host,
            db_user,
            password,
            dbport))
    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    g2d = Gpx2db(conn)

    # TODO: move database initialization up
    if delete_mode:
        g2d.init_db(drop=True)

    # loop files
    for gpx_file_name in filelist:

        gpx_fd = open(gpx_file_name, 'r')
        gpx_o = gpxpy.parse(gpx_fd)
        src_info = os.path.basename(gpx_file_name)
        print("Loading {}".format(src_info))
        g2d.load_gpx_file(gpx_o, src=src_info)
