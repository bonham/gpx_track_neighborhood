import pytest
from gpx2db.gpx2dblib import Gpx2db
import gpxpy
from os import path
import glob

my_dir = path.dirname(__file__)


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


@ pytest.fixture(
    params=glob.glob('C:/Users/Michael/poc/gisprojekt/tracks/db2020/*.gpx'))
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


# pytest_plugins = ['pytest_profiling']


class TestGpx2Db:
    # @pytest.mark.skip
    def test_create_schema(self, dbconn, gpxpy_obj):

        g2d = Gpx2db(dbconn, "MYSCHEMA")
        g2d.create_schema()

        executefunc = g2d.cur.execute

        for i, v in enumerate(executefunc.call_args_list):
            sql = v.args[0]
            assert "MYSCHEMA" in sql.upper()

        g2d.load_gpx_file(gpxpy_obj(1), "fakehash1", src="file1")
        g2d.load_gpx_file(gpxpy_obj(1), "fakehash2", src="file2")

    def test_big(self, dbconn, gpxpy_bigiterator):

        g2d = Gpx2db(dbconn)

        (fname, gpx_obj) = gpxpy_bigiterator
        g2d.load_gpx_file(gpx_obj, src=fname)
