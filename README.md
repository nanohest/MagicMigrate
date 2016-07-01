MagicMigrate
======

MagicMigrate is forked from [Godwit](https://github.com/perliedman/godwit),
it aims to be a super duper slim and minimalistic tool to migrate databases.

Currently, it supports [Microsoft SQL Server](https://www.microsoft.com/en-us/server-cloud/products/sql-server/),
using [pymssql](http://pymssql.org/en/latest/).

Installing
----------

To install from source, MagicMigrate uses distutils, run this:

```shell
python setup.py install
```

Usage
-----

Migration is done through a number of SQL scripts. These scripts should be
put into their own directory (see the ```example``` directory). The scripts
must use the extension ```.sql```.

Migration can then be run from the command line:

```shell
python -m MagicMigrate [host] [database] [username] [password] [script-dir] [version]
```

This will connect to the provided ```host``` and ```database```, and migrate
the database to the provided ```version``` using the scripts in ```script-dir```.

SQL Script versioning
---------------------

Scripts must be given an integer version number, right after the first ```_``` (underscore), and before another ```_``` or a ```.``` (punctuation mark).  
What comes before the first ```_```, and after the second ```_```, or first ```.```, does not matter much, as long as the file ends on ```.sql```  
So, to give a few examples, these would all work:
```
Update_0.sql
update_01.sql
updat0rz_002.sql
update_003_customer_table_index.sql
update_4.create_delivery_table.sql
dropIndex_05_deliveryTable.sql
```

Versions will be kept in numeric order.

Comments
--------

If the first line of your SQL script starts with ```--```, excluding whitespace and line breaks, the rest of the line will be stored as a description of your migration, alongside the versioning.
