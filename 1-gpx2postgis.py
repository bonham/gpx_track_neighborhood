import sys
import argparse
import glob
import os
import subprocess
import psycopg2 as pg2
from gpx2db import Gpx2db
import gpxpy


if sys.version_info < (3, 6):
    raise RuntimeError("You must use python 3.6, You are using python {}.{}.{}".format(
        *sys.version_info[0:3]))

# constants

PG_USER = "postgres"
PG_ADMIN_DB = "postgres"
OGR2OGR = os.environ.get('OGR2OGR') or "ogr2ogr"


def main():

    # pre check system environment
    pre_check()

    # parse args
    (database_name, host, user, password, dbport, directory, delete_db) = a_parse()

    # get gpx filenames
    gpx_filelist = getfiles(directory)
    print("Number of gpx files: {}".format(len(gpx_filelist)))

    # import files into database
    if delete_db:
        print("(Re-) creating database {}".format(database_name))
    else:
        print("Appending to database {}".format(database_name))

    gpximport(gpx_filelist, database_name, delete_db,
              host, user, password, dbport)


# --------------------------------
def a_parse():
    parser = argparse.ArgumentParser(
        description='Load GPX files in specified directory into postgis database'
    )
    parser.add_argument('source_directory')
    parser.add_argument('database')
    parser.add_argument(
        '--createdb',
        action='store_true',
        help="Create the database. If it does already exist, the old db will be overwritten!")
    parser.add_argument(
        '-n',
        '--host',
        default='localhost',
        help="Database Host")
    parser.add_argument(
        '-u',
        '--user',
        default=PG_USER,
        help="Database user")
    parser.add_argument(
        '-p',
        '--password',
        default='',
        help="Database Password")
    parser.add_argument(
        '--port',
        default='5432',
        help="Database Port")
    args = parser.parse_args()

    return (
        args.database,
        args.host,
        args.user,
        args.password,
        args.port,
        args.source_directory,
        args.createdb)


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


def gpximport(filelist, database_name, delete_mode, host, db_user, password, dbport):

    if delete_mode:

        # connect to system database 'postgres' first
        sysDBconn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                PG_ADMIN_DB,
                host,
                db_user,
                password,
                dbport))
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
        "dbname={} host={} user={} password={} port={}".format(
            database_name,
            host,
            db_user,
            password,
            dbport))
    conn.set_isolation_level(pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    exf = ExecuteSQLFile(conn)

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


if __name__ == "__main__":
    # execute only if run as a script
    main()
