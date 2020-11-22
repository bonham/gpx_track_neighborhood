import sys
import argparse
import glob
import os
import subprocess
import psycopg2 as pg2

if sys.version_info < (3, 6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(
        *sys.version_info[0:3]))

# constants

PG_USER = "postgres"
OGR2OGR = "ogr2ogr"


def main():

    # pre check system environment
    pre_check()

    # parse args
    (directory, database_name, appendmode, host, user, password) = a_parse()

    # get gpx filenames
    gpx_filelist = getfiles(directory)
    print("Number of gpx files: {}".format(len(gpx_filelist)))

    # import files into database
    print("(Re-) creating database {}".format(database_name))
    ogrimport(gpx_filelist, database_name, appendmode, host, user, password)


# --------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
        description='Load GPX files in specified directory into postgis database'
    )
    parser.add_argument('source_directory')
    parser.add_argument('database')
    parser.add_argument(
        '-a',
        '--append',
        action='store_true',
        help="Do not delete database, but append track to existing database")
    parser.add_argument(
        '-n',
        '--host',
        help="Database Host")
    parser.add_argument(
        '-u',
        '--user',
        help="Database user")
    parser.add_argument(
        '-p',
        '--password',
        help="Database Password")
    args = parser.parse_args()

    database_name = args.database
    directory = args.source_directory
    appendmode = args.append
    return directory, database_name, appendmode, args.host, args.user, args.password


# --------------------------------
def getfiles(directory):

    normdir = os.path.abspath(directory)
    globexp = os.path.join(normdir, "*.gpx")
    dirs = glob.glob(globexp)

    return dirs


def pre_check():

    try:
        subprocess.call((OGR2OGR, "--help"),
                        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except FileNotFoundError as e:
        print("Error: The command {} could not be found on your system".format(OGR2OGR))
        sys.exit(1)


class ExecuteSQLFile:

    def __init__(self, connection):

        SQL_RELATIVE_DIR = "sql"

        self.sqlBase = os.path.join(
            os.path.dirname(__file__),
            SQL_RELATIVE_DIR
        )

        self.conn = connection
        self.cursor = connection.cursor()

    def fpath(self, fname):

        p = os.path.join(
            self.sqlBase,
            fname)

        return p

    def execFile(self, fname, sqlArgs=[], commit=True):

        fpath = self.fpath(fname)

        #print("Execute SQL file {}".format(fpath))

        with open(fpath, "r") as f:
            sql = f.read()
            self.cursor.execute(sql, sqlArgs)

        if commit:
            self.conn.commit()


def ogrimport(filelist, database_name, appendmode, host, user, password):

    # connect to postgres db
    deleteDatabase = not appendmode

    db_user = PG_USER or user

    if (deleteDatabase):

        # connect to system database 'postgres' first
        sysDBconn = pg2.connect(
            "dbname={} host={} user={} password={}".format(
                "postgres",
                host,
                db_user,
                password))
        sysDBconn.set_isolation_level(
            pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        sysDBcur = sysDBconn.cursor()

        # sql setup
        sql1 = "drop database if exists {0}".format(database_name)
        sql2 = "create database {0}".format(database_name)

        sysDBcur.execute(sql1)
        sysDBcur.execute(sql2)
        sysDBconn.close()

    # connect to newly created db
    conn = pg2.connect(
        "dbname={} host={} user={} password={}".format(
            database_name,
            host,
            db_user,
            password))
    conn.set_isolation_level(pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    exf = ExecuteSQLFile(conn)

    if (deleteDatabase):
        # create postgis extension
        sql3 = "create extension postgis"
        cur.execute(sql3)

        # pre-create layer tables
        exf.execFile('sql_0_0_create_track_files_table.sql')
        exf.execFile('sql_0_1_create_all_tracks_table.sql')
        exf.execFile('sql_0_2_create_all_track_points_table.sql')

    # ogr
    ogr_connstring = "PG:dbname={} host={} user={} password={}".format(
        database_name,
        host,
        db_user,
        password)

    # loop files
    for gpxfile in filelist:

        cmd = (
            OGR2OGR,
            "-append",
            "-f",
            "PostgreSQL",
            "-preserve_fid",
            "-overwrite",
            ogr_connstring,
            gpxfile,
            "track_points",
            "tracks"
        )

        sql4 = "select nextval('track_files_seq')"
        cur.execute(sql4)
        file_id = cur.fetchone()[0]
        print()
        print("=== Track file number {}".format(file_id))

        print("=== Processing {} with command {}".format(gpxfile, " ".join(cmd)))
        subprocess.check_call(cmd)

        exf.execFile('sql_0_5_insert_track_file.sql', [file_id, gpxfile])
        exf.execFile('sql_0_6_insert_all_tracks.sql', [file_id])
        exf.execFile('sql_0_7_insert_all_trackpoints.sql', [file_id])


if __name__ == "__main__":
    # execute only if run as a script
    main()
