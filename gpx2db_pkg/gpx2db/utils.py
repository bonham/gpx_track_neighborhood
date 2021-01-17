import os
import logging
import glob
logger = logging.getLogger(__name__)


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


def getfiles(directory):

    normdir = os.path.abspath(directory)
    globexp = os.path.join(normdir, "*.gpx")
    dirs = glob.glob(globexp)

    return dirs
