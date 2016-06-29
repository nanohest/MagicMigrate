from os import listdir
from datetime import datetime as dt
import argparse
import hashlib
import os.path

class MigrateSql:
    def __init__(self, adaptor, script_dir, commit=True):
        self.adaptor    = adaptor
        self.script_dir = script_dir
        self.commit     = commit

    def initialize_database_versioning(self):
        print("Initializing database for versioning")
        cur = self.adaptor.conn.cursor()
        try:
            cur.execute(self.adaptor.create_version_table)
        except Exception:
            self.adaptor.conn.rollback()
            print "magmig_schema_version table could not be created"
            print "Check connection settings and permissions"
            raise

    def get_current_version(self):
        cur = self.adaptor.conn.cursor()
        try:
            try:
                cur.execute(self.adaptor.query_curr_version)
                return cur.fetchone()[0]
            except:
                self.adaptor.conn.rollback()
                return None
        finally:
            cur.close()

    def migrate(self, to_version=None):
        cur = self.adaptor.conn.cursor()
        try:
            for migration_script in self._get_migration_scripts(self.get_current_version(), to_version):
                with open(os.path.join(self.script_dir, migration_script), 'r') as script_file:
                    try:
                        print "Migrating to %s" % migration_script
                        # read file
                        content = script_file.read()
                        # if first line is a comment
                        # we'll treat it as a description
                        first_line = content.lstrip().split('\n', 1)[0]
                        description = None
                        if first_line[0:2] == '--':
                            description = first_line.lstrip()[2:]

                        # apply changes
                        cur.execute(content)
                        version = str.split(os.path.splitext(migration_script)[0],'_')[1]
                        cur.execute(self.adaptor.insert_version_rec,(version,
                                                                     migration_script,
                                                                     hashlib.sha224(content).hexdigest(),
                                                                     description)
                        )
                    except Exception:
                        self.adaptor.conn.rollback()
                        print "Migration failed in script %s" % migration_script
                        raise

            if self.commit:
                self.adaptor.conn.commit()
            else:
                self.adaptor.conn.rollback()
                print "Migration was rolled back since running in dry-run mode."
        finally:
            cur.close()

    def _get_migration_scripts(self, from_version=None, to_version=None):
        scripts = [x for x in listdir(self.script_dir)
            if x.endswith('.sql') and
            (from_version is None or str.split(x,'_')[1] > ("%s.sql" % from_version)) and
            (to_version is None or str.split(x,'_')[1] <= ("%s.sql" % to_version))]

        scripts.sort()
        return scripts

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='If set, will rollback any migrations after they complete.')
    parser.add_argument('--initdb', action='store_true', help='If set, will initialize db with magmig_schema_version table.')
    parser.add_argument('--force', action='store_true', help='Execute migrations, even if previously run scripts have changed')
    parser.add_argument('-adaptor', default='mssql')
    parser.add_argument('-host')
    parser.add_argument('-database')
    parser.add_argument('-username')
    parser.add_argument('-password')
    parser.add_argument('-scriptdir')
    parser.add_argument('--version', default=None)
    args = parser.parse_args(argv[1:len(argv)])

    # Import and load specific db adaptor
    fully_qualified = "adaptors.%s.DbAdaptor" % args.adaptor
    parts = fully_qualified.split('.')
    m = __import__( ".".join(parts[:-1]) )
    for comp in parts[1:]:
        m = getattr(m, comp)
    adaptor = m(username=args.username,
                password=args.password,
                database=args.database,
                hostname=args.host,
                dry_run=args.dry_run)

    # Now, let's get busy
    try:
        migrator = MigrateSql(adaptor, args.scriptdir, commit=not args.dry_run)
        if args.initdb:
            migrator.initialize_database_versioning()
        migrator.migrate(args.version)
    finally:
        adaptor.conn.close()

if __name__ == '__main__':
    from sys import argv

    main(argv)
