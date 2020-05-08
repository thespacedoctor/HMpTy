

```bash 
    
    Documentation for HMpTy can be found here: http://HMpTy.readthedocs.org
    
    Usage:
        hmpty htmid <level> <ra> <dec>
        hmpty [-f] index <tableName> <primaryIdCol> <raCol> <decCol> (-s <pathToSettingsFile>|--host <host> --user <user> --passwd <passwd> --dbName <dbName>)
        hmpty search <tableName> <raCol> <decCol> <ra> <dec> <radius> (-s <pathToSettingsFile>|--host <host> --user <user> --passwd <passwd> --dbName <dbName>) [(-r <format>|-r mysql <resultsTable>)]
    
    Options:
        index                 add HTMids to database table
        search                perform a conesearch on a database table
        htmid                 generate the htmID at the given coordinates for the give HTM level
    
        tableName                                                       name of the table to add the HTMids to
        primaryIdCol                                                    the name of the unique primary ID column of the database table
        raCol                                                           name of the table column containing the right ascension
        decCol                                                          name of the table column containing the declination
        ra                                                              the right ascension of the centre of the conesearch circle or coordinate set
        dec                                                             the declination of the centre of the conesearch circle or coordinate set
        radius                                                          the radius of the conesearch circle (arcsec)
        level                                                           the HTM level required
    
        -f, --force                                                     force a regeneration of all HTMIDs
        -h, --help                                                      show this help message
        -v, --version                                                   show version
        -s <pathToSettingsFile>, --settings <pathToSettingsFile>        path to a settings file containing the database credentials
        --host <host>                                                   database host address
        --user <user>                                                   database username
        --passwd <passwd>                                               database password
        --dbName <dbName>                                               database name
        -r <format>, --render <format>                                  select a format to render your results in
    

```
