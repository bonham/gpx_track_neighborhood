from gpx2db import initdb
from unittest.mock import Mock


def test_initdb_cd(monkeypatch):

    testargs = ['', 'cd', 'newdbname']
    monkeypatch.setattr("sys.argv", testargs)
    monkeypatch.setattr("gpx2db.initdb.connect_nice", Mock())
    monkeypatch.setattr("gpx2db.initdb.create_db", Mock())
    monkeypatch.setattr("gpx2db.initdb.drop_db", Mock())
    initdb.main()


def test_initdb_cs(monkeypatch):

    testargs = ['', 'cs', 'existingdb', 'newschema']
    monkeypatch.setattr("sys.argv", testargs)
    monkeypatch.setattr("gpx2db.initdb.connect_nice", Mock())
    monkeypatch.setattr("gpx2db.initdb.Gpx2db", Mock())
    initdb.main()
