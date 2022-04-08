from gpx2db.proximity_calc import Transform


class TestInitProximatorSchema:
    def test_create_structure_has_schema(self, dbconn):
        tf = Transform(dbconn, 'MYSCHEMA')
        tf.create_structure()

        executefunc = tf.conn.cursor().execute

        for i, v in enumerate(executefunc.call_args_list):
            sql = v.args[0]
            assert "MYSCHEMA" in sql.upper()
