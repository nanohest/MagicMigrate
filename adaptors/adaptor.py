
class Adaptor:
    def __init__(self,init_table,curr_ver,insert_ver,conn):
        self.create_version_table = init_table
        self.query_curr_version   = curr_ver
        self.insert_version_rec   = insert_ver
        self.conn                 = conn
