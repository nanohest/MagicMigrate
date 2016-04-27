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
must use the extension ```.sql```. The name of the file (without the .sql
extension) is called the "version" of this script. Versions are ordered in
lexicographic order.

Migration can then be run from the command line:

```shell
python -m MagicMigrate [host] [database] [username] [password] [script-dir] [version]
```

This will connect to the provided ```host``` and ```database```, and migrate
the database to the provided ```version``` using the scripts in ```script-dir```.
