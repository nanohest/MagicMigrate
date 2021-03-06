import pymssql
from adaptors.adaptor import Adaptor

class DbAdaptor(Adaptor):

    def __init__(self,username,password,database,hostname,dry_run):
        query_curr_version   = "SELECT TOP 1 [version] FROM [magmig_schema_version] ORDER BY [version] DESC"
        insert_version_rec   = "INSERT INTO [magmig_schema_version] (version,script,checksum,description) VALUES (%s,%s,%s,%s)"
        create_version_table = """
            CREATE TABLE magmig_schema_version (
                [version] int not null unique,
                [script] varchar(255),
                [checksum] varchar(255),
                [description] varchar(255),
                [datetime] datetime2 default current_timestamp not null
            )
        """
        conn = pymssql.connect(host=hostname,
                               user=username,
                               password=password,
                               database=database,
                               autocommit=not dry_run)
        Adaptor.__init__(self,
                         init_table = create_version_table,
                         curr_ver = query_curr_version,
                         insert_ver = insert_version_rec,
                         conn = conn)
