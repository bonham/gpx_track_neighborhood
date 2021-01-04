import pytest
from mock import Mock
from gpx2db import Gpx2db
import gpxpy
from os import path, environ
import psycopg2 as pg2
import glob

my_dir = path.dirname(__file__)


@pytest.fixture
def dbconn():

    # Set this to False if you have a real backend ( empty DB )
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
        syg2dBconn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                "test3", "localhost", "postgres", password, 5432
            )
        )
        return syg2dBconn


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


@ pytest.fixture(params=glob.glob('C:/Users/Michael/poc/gisprojekt/tracks/db2020/*.gpx'))
def gpxpy_bigiterator(request):
    "This only works if directory is present"
    "Returns iterator which yields list of gpxpy objs"

    gpx_file = open(request.param, 'r')
    gpx_object = gpxpy.parse(gpx_file)
    r = (
        path.basename(request.param),
        gpx_object
    )
    yield r


#pytest_plugins = ['pytest_profiling']


class TestGpx2Db:
    # @pytest.mark.skip
    def test1(self, dbconn, gpxpy_obj):

        g2d = Gpx2db(dbconn)
        g2d.init_db(drop=True)
        g2d.load_gpx_file(gpxpy_obj(1), src="file1")
        g2d.load_gpx_file(gpxpy_obj(1), src="file2")

    def test_big(self, dbconn, gpxpy_bigiterator):

        g2d = Gpx2db(dbconn)
        # g2d.init_db(drop=True)

        (fname, gpx_obj) = gpxpy_bigiterator
        g2d.load_gpx_file(gpx_obj, src=fname)
