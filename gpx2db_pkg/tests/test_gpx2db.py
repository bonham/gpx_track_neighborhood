import pytest
from mock import Mock
from gpx2db import SetupDb
import gpxpy
from os import path, environ
import psycopg2 as pg2

my_dir = path.dirname(__file__)


@pytest.fixture
def dbconn():
    mocking = False

    if mocking:
        conn = Mock()
        row1 = (1, 'peter')
        row2 = (2, 'paul')
        conn.cursor.return_value.fetchall.return_value = [row1, row2]
        conn.cursor.return_value.fetchone.return_value = row1
        return conn

    else:
        password = environ.get('PGPASS')
        sysDBconn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                "test3", "localhost", "postgres", password, 5432
            )
        )
        return sysDBconn


@ pytest.fixture
def gpxpy_obj():

    def gpx_creator(i):
        fname = path.join(
            my_dir,
            'test_data',
            'file{}.gpx'.format(i)
        )
        gpx_file = open(fname, 'r')
        gpx_o = gpxpy.parse(gpx_file)
        return gpx_o

    return gpx_creator


class TestGpx2Db:

    def test1(self, dbconn, gpxpy_obj):

        sd = SetupDb(dbconn)
        sd.init_db(drop=True)
        sd.load_gpx_file(gpxpy_obj(1), src="file1")
