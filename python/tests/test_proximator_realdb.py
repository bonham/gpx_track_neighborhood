from gpx2db import (
    initdb,
    initdb_proximator,
    proximity_calc
)
from os import getcwd


def test_cycle(monkeypatch):

    # create db
    testargs = ['', 'cd', 't1']
    monkeypatch.setattr("sys.argv", testargs)
    initdb.main()

    testargs = ['', 'cs', 't1', 's1']
    monkeypatch.setattr("sys.argv", testargs)
    initdb.main()

    testargs = ['', 't1', 's1']
    monkeypatch.setattr("sys.argv", testargs)
    initdb_proximator.main()

    print(getcwd())
    # TODO: test data should be in git
    testargs = [
        '',
        '..\\..\\Tracks\\Regiotours\\Regiotour-2020\\Bernd',
        't1',
        's1']
    monkeypatch.setattr("sys.argv", testargs)
    proximity_calc.main()
