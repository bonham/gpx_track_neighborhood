import pytest
from os import environ
import psycopg2 as pg2
from unittest.mock import Mock

@pytest.fixture
def dbconn():

    # Set this to False if you have a real backend ( empty DB )
    mocking = True

    if mocking:
        conn = Mock(name="mockconn")
        cursor = Mock(name="mockcur")
        cursor.return_value.__enter__ = Mock(name="mockenterfunc")
        cursor.return_value.__exit__ = Mock(name="exitfunc")
        row1 = (1, 'peter')
        row2 = (2, 'paul')
        cursor.return_value.fetchall.return_value = [row1, row2]
        cursor.return_value.fetchone.return_value = row1
        conn.cursor = cursor
        return conn

    else:
        password = environ.get('PGPASS')
        syg2dBconn = pg2.connect(
            "dbname={} host={} user={} password={} port={}".format(
                "test3", "localhost", "postgres", password, 5432
            )
        )
        return syg2dBconn
