from gpx2db import (
    initdb,
    gpx2postgres,
    list_tracks,
    delete_track
)


def test_non_proximity(monkeypatch):

    # create db
    testargs = ['', 'cd', 't1']
    monkeypatch.setattr("sys.argv", testargs)
    initdb.main()

    testargs = ['', 'cs', 't1', 's1']
    monkeypatch.setattr("sys.argv", testargs)
    initdb.main()

    # TODO: test data should be in git
    testargs = [
        '',
        '..\\..\\Tracks\\Regiotours\\Regiotour-2020\\Bernd',
        't1',
        's1']
    monkeypatch.setattr("sys.argv", testargs)
    gpx2postgres.main()

    testargs = [
        '',
        't1',
        's1']
    monkeypatch.setattr("sys.argv", testargs)
    list_tracks.main()

    testargs = [
        '',
        't1',
        's1',
        '1']
    monkeypatch.setattr("sys.argv", testargs)
    delete_track.main()
