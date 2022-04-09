from gpx2db import (
    initdb,
    initdb_proximator,
    proximity_calc,
    export_geojson
)


def test_proximity_core(monkeypatch):

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

    # TODO: test data should be in git
    testargs = [
        '',
        '..\\..\\Tracks\\Regiotours\\Regiotour-2020\\Bernd',
        't1',
        's1']
    monkeypatch.setattr("sys.argv", testargs)
    proximity_calc.main()

    testargs = [
        '',
        't1',
        's1',
        'testlabel']
    monkeypatch.setattr("sys.argv", testargs)
    export_geojson.main()
