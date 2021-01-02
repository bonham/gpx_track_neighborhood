import pytest
from mock import Mock
from gpx2db import SetupDb


@pytest.fixture
def dbconn():
    "Mocked connection"
    return Mock()


@pytest.fixture
def gpxpy_obj():
    return Mock()


class TestGpx2Db:

    def test1(self, dbconn, gpxpy_obj):

        sd = SetupDb(dbconn)
        sd.init_db()
        sd.load_gpx_file(gpxpy_obj)
