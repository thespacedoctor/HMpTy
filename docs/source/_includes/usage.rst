Usage
======

.. code-block:: bash 
   
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
    