import os
import sys
import logging
import glob
import psycopg2 as pg2
import argparse
import re

logger = logging.getLogger(__name__)

PG_ADMIN_DB = 'postgres'


class ExecuteSQLFile:

    def __init__(self, connection, base_dir='', schema=None):

        self.base_dir = base_dir
        self.schema = schema

        self.conn = connection
        self.cur = connection.cursor()

    def fpath(self, fname):

        p = os.path.join(
            self.base_dir,
            fname)

        return p

    def execFile(self, fname, sqlArgs=[], args=(), commit=True):

        fpath = self.fpath(fname)

        with open(fpath, "r") as f:
            sqltemplate = f.read()
            logging.debug("Args: {}".format(args))
            sql = sqltemplate.format(schema=self.schema, *args)
            logging.debug(sql)
            self.cursor().execute(sql, sqlArgs)

        if commit:
            self.conn.commit()

    def cursor(self):
        return self.cur


def vac(conn, table):
    cur = conn.cursor()
    cur.execute("vacuum analyze {}".format(table))


def getfiles(dir_or_file):

    if not os.path.exists(dir_or_file):
        logger.error("File or directory {} does not exist.".format(
            dir_or_file
        ))
        sys.exit(1)

    if os.path.isfile(dir_or_file):
        fname = dir_or_file
        return [fname]

    else:
        directory = dir_or_file
        normdir = os.path.abspath(directory)
        globexp = os.path.join(normdir, "*.gpx")
        filelist = glob.glob(globexp)

        return filelist


def connect_nice(connstring):
    "Connect and print nice error and exit 1 if db does not exist"
    try:
        conn = pg2.connect(connstring)
    except pg2.OperationalError as e:
        errmsg = e.args[0]
        m = re.search(r'database (.*?) does not exist', errmsg)
        if m:
            logger.error((
                "Database {} does not exist. "
                "You must create the database first or choose existing DB"
                ).format(m.group(1)))
            sys.exit(1)
        else:
            print(re)
            print(e)
            raise
    else:
        return conn


def drop_db(database_name_to_drop, connstring):

    sql_drop = "drop database if exists {0}".format(database_name_to_drop)
    exec_with_connect(sql_drop, connstring)


def create_db(database_name, connstring):

    sql_create = "create database {0}".format(database_name)
    exec_with_connect(sql_create, connstring)


def exec_with_connect(sql, connstring):

    conn = pg2.connect(connstring)
    conn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    cur = conn.cursor()

    cur.execute(sql)
    conn.close()


def setup_logging(debug):

    if debug:
        loglevel = logging.DEBUG
        fmt = (
            '%(asctime)-15s - %(filename)s '
            '%(lineno)d - %(levelname)s - %(message)s')

    else:
        loglevel = logging.INFO
        fmt = '%(levelname)-7s: %(message)s'

    logger = logging.getLogger()
    logger.setLevel(loglevel)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt))

    logger.addHandler(ch)

    return logger


def getDbParentParser():

    databaseArgParser = argparse.ArgumentParser(add_help=False)

    # set password default from env variable
    if 'PGPASSWORD' in os.environ:
        pass_required = False
        databaseArgParser.set_defaults(password=os.environ['PGPASSWORD'])

    else:
        pass_required = True

    databaseArgParser.add_argument(
        '-n',
        '--host',
        help="Database Host")
    databaseArgParser.add_argument(
        '-u',
        '--user',
        help="Database user")
    databaseArgParser.add_argument(
        '-p',
        '--password',
        required=pass_required,
        help="Database Password")
    databaseArgParser.add_argument(
        '--port',
        help="Database Port")

    return databaseArgParser


def read_snip_coords():
    "Read list of coordinates from env"
    " "
    "Format: $env:GPX_SNIP_COORDS = 'D.dddd,D.dddd D.dddd,D.dddd'"
    "list of decimal degrees lat,lon separated by comma,"
    "multiple coordinates separated by space. Example"
    " "
    "$env:GPX_SNIP_COORDS = '49.213038,3.553038 49.6739,6.46637' "

    VARNAME = 'GPX_SNIP_COORDS'
    return_list = []

    if VARNAME not in os.environ:
        return []

    # split by whitespace
    pair_list = os.environ[VARNAME].split()

    # regex pattern for pair
    latlon_pattern = re.compile(
        r'^(\d+\.\d+),(\d+\.\d+)$'
    )

    for pair in pair_list:

        m = latlon_pattern.match(pair)
        if m:
            lat = m.group(1)
            lon = m.group(2)
            return_list.append((lat, lon))

    return return_list


def create_connection_string(database_name, args):
    "set defaults here"

    connstring = "dbname=" + database_name

    if args.host:
        connstring += " host=" + args.host
    elif "PGHOST" not in os.environ:
        connstring += " host=localhost"

    if args.user:
        connstring += " user=" + args.user
    elif "PGUSER" not in os.environ:
        connstring += " user=postgres"

    if args.password:
        connstring += " password=" + args.password

    if args.port:
        connstring += " port=" + args.port

    logger.debug("Connection string: {}".format(connstring))
    return connstring
