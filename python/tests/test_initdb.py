from gpx2db import initdb
from unittest import mock
import sys


def test_initdb():

    testargs = ['', 'cd', 'newdbname']

    with mock.patch.object(sys, 'argv', testargs):
        initdb.a_parse()
