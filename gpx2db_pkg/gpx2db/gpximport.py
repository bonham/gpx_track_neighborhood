import os
import psycopg2 as pg2
import gpxpy
from .utils import ExecuteSQLFile
from .gpx2dblib import Gpx2db

PG_ADMIN_DB = "postgres"
PG_ADMIN_DB_USER = "postgres"


def gpximport(filelist, database_name, delete_mode, host, db_user, password, dbport):

    if delete_mode:

        # connect to system database 'postgres' first
        sysDBconn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                PG_ADMIN_DB,
                host,
                PG_ADMIN_DB_USER,
                password,
                dbport))
        sysDBconn.set_isolation_level(
            pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

        sysDBcur = sysDBconn.cursor()

        # sql setup
        sql1 = "drop database if exists {0}".format(database_name)
        sql2 = "create database {0}".format(database_name)

        sysDBcur.execute(sql1)
        sysDBcur.execute(sql2)
        sysDBconn.close()

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
    sqldir = os.path.join(os.path.dirname(__file__), 'sql')
    ExecuteSQLFile(conn, base_dir=sqldir)

    g2d = Gpx2db(conn)

    if delete_mode:
        g2d.init_db(drop=True)

    # loop files
    for gpx_file_name in filelist:

        gpx_fd = open(gpx_file_name, 'r')
        gpx_o = gpxpy.parse(gpx_fd)
        src_info = os.path.basename(gpx_file_name)
        print("Loading {}".format(src_info))
        g2d.load_gpx_file(gpx_o, src=src_info)
