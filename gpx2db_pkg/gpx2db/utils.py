import os
import sys
import logging
import glob
import psycopg2 as pg2
import argparse

logger = logging.getLogger(__name__)

PG_ADMIN_DB = 'postgres'
PG_ADMIN_DB_USER = 'postgres'


class ExecuteSQLFile:

    def __init__(self, connection, base_dir=''):

        self.base_dir = base_dir

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
            sql = sqltemplate.format(*args)
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


def drop_db(
        database_name_to_drop, admin_db_password,
        host='localhost', dbport=5432):

    # connect to system database 'postgres' first
    sysDBconn = pg2.connect(
        "dbname={} host={} user={} password={} port={}".format(
            PG_ADMIN_DB,
            host,
            PG_ADMIN_DB_USER,
            admin_db_password,
            dbport))
    sysDBconn.set_isolation_level(
        pg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # type: ignore

    sysDBcur = sysDBconn.cursor()

    # sql setup
    sql1 = "drop database if exists {0}".format(database_name_to_drop)
    sql2 = "create database {0}".format(database_name_to_drop)

    sysDBcur.execute(sql1)
    sysDBcur.execute(sql2)
    sysDBconn.close()


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

    PG_USER = 'postgres'

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
        default='localhost',
        help="Database Host")
    databaseArgParser.add_argument(
        '-u',
        '--user',
        default=PG_USER,
        help="Database user")
    databaseArgParser.add_argument(
        '-p',
        '--password',
        required=pass_required,
        help="Database Password")
    databaseArgParser.add_argument(
        '--port',
        default='5432',
        help="Database Port")

    return databaseArgParser
