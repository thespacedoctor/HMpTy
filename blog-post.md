HMpTy
=====

*Tools for working with Hierarchical Triangular Meshes (HTMs). Generate HTMIDs, crossmatch sky-coordinates via angular separation and more*.

Usage
=====

``` sourceCode
hmpty table <tableName> <primaryIdCol> <raCol> <decCol> -s <pathToSettingsFile>
hmpty table --host=<host> --user=<user> --passwd=<passwd> --dbName=<dbName> <tableName> <primaryIdCol> <raCol> <decCol> [-s <pathToSettingsFile>]

COMMANDS
========
table                 add HTMids to database table

ARGUMENTS
=========
tableName             name of the table to add the HTMids to
primaryIdCol          the name of the unique primary ID column of the database table
raCol                 name of the talbe column containing the right ascension
decCol                name of the talbe column containing the declination
host                  database host address
user                  database username
passwd                database password
dbName                database name

FLAGS
=====
-h, --help            show this help message
-s, --settings        the settings file
```

Installation
============

The easiest way to install HMpTy us to use `pip`:

``` sourceCode
pip install HMpTy
```

Or you can clone the [github repo](https://github.com/thespacedoctor/HMpTy) and install from a local version of the code:

``` sourceCode
git clone git@github.com:thespacedoctor/HMpTy.git
cd HMpTy
python setup.py install
```

To upgrade to the latest version of HMpTy use the command:

``` sourceCode
pip install HMpTy --upgrade
```

Documentation
=============

Documentation for HMpTy is hosted by [Read the Docs](http://HMpTy.readthedocs.org/en/stable/) (last [stable version](http://HMpTy.readthedocs.org/en/stable/) and [latest version](http://HMpTy.readthedocs.org/en/latest/)).

Tutorial
========
