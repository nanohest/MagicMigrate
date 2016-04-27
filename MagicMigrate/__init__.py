from os import listdir
import os.path
from datetime import datetime as dt
import argparse
import pymssql
import hashlib

class Migrate:
    def __init__(self, conn, script_dir, commit=True):
        self.conn = conn
        self.script_dir = script_dir
        self.commit = commit

    def initialize_database_versioning(self):
        print("Initializing database for versioning")
        create_version_table = """
            create table magmig_schema_version (
                version int not null unique,
                hashvalue varchar(100),
                description varchar(255),
                datetime datetime2 default current_timestamp not null
            )
        """
        cur = self.conn.cursor()
        try:
            cur.execute(create_version_table)
        except Exception:
            self.conn.rollback()
            print "magmig_schema_version table could not be created"
            print "Check connection settings and permissions"
            raise

    def get_current_version(self):
        cur = self.conn.cursor()
        try:
            try:
                cur.execute(self.query_curr_version)
                return cur.fetchone()[0]
            except:
                self.conn.rollback()
                return None
        finally:
            cur.close()

    def migrate(self, to_version=None):
        cur = self.conn.cursor()
        try:
            for migration_script in self._get_migration_scripts(self.get_current_version(), to_version):
                with open(os.path.join(self.script_dir, migration_script), 'r') as script_file:
                    try:
                        print "Migrating to %s" % migration_script
                        content = script_file.read()
                        cur.execute(content)
                        filename = os.path.splitext(migration_script)[0]
                        cur.execute(self.query_insert_version, (str.split(filename,'_')[1],
                                                                hashlib.sha224(content).hexdigest())
                        )
                    except Exception:
                        self.conn.rollback()
                        print "Migration failed in script %s" % migration_script
                        raise

            if self.commit:
                self.conn.commit()
            else:
                self.conn.rollback()
                print "Migration was rolled back since running in dry-run mode."
        finally:
            cur.close()

    def _get_migration_scripts(self, from_version=None, to_version=None):
        scripts = [x for x in listdir(self.script_dir)
            if x.endswith('.sql') and
            (from_version is None or x > ("%s.sql" % from_version)) and
            (to_version is None or x <= ("%s.sql" % to_version))]

        scripts.sort()
        return scripts

class MigrateSql(Migrate):
    query_curr_version = 'select top 1 version from magmig_schema_version order by version desc'
    query_insert_version = 'insert into magmig_schema_version (version,hashvalue) values (%s,%s)'

    def __init__(self, conn, script_dir, commit):
        Migrate.__init__(self, conn, script_dir, commit)

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='If set, will rollback any migrations after they complete.')
    parser.add_argument('--initdb', action='store_true', help='If set, will initialize db with magmig_schema_version table.')
    parser.add_argument('-host')
    parser.add_argument('-database')
    parser.add_argument('-username')
    parser.add_argument('-password')
    parser.add_argument('-scriptdir')
    parser.add_argument('--version', default=None)
    args = parser.parse_args(argv[1:len(argv)])

    conn = pymssql.connect(host=args.host,
                           user=args.username,
                           password=args.password,
                           database=args.database,
                           autocommit=not args.dry_run)
    try:
        m = MigrateSql(conn, args.scriptdir, commit=not args.dry_run)
        if args.initdb:
            m.initialize_database_versioning()
        m.migrate(args.version)
    finally:
        conn.close()

if __name__ == '__main__':
    import pymssql
    from sys import argv

    main(argv)
