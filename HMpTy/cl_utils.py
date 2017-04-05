#!/usr/local/bin/python
# encoding: utf-8
"""
Documentation for HMpTy can be found here: http://HMpTy.readthedocs.org/en/stable


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

"""
################# GLOBAL IMPORTS ####################


import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from HMpTy.mysql import add_htm_ids_to_mysql_database_table, conesearch
# from ..__init__ import *


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="DEBUG",
        options_first=False,
        projectName="HMpTy"
    )
    arguments, settings, log, dbConn = su.setup()

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    # CALL FUNCTIONS/OBJECTS
    if index:
        add_htm_ids_to_mysql_database_table(
            raColName=raCol,
            declColName=decCol,
            tableName=tableName,
            dbConn=dbConn,
            log=log,
            primaryIdColumnName=primaryIdCol,
            reindex=forceFlag
        )

    if search:
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName=tableName,
            columns=False,
            ra=ra,
            dec=dec,
            radiusArcsec=float(radius),
            separations=True,
            distinct=False,
            sqlWhere=False
        )
        matchIndies, matches = cs.search()
        if not renderFlag:
            print matches.table()
        elif renderFlag == "json":
            print matches.json()
        elif renderFlag == "csv":
            print matches.csv()
        elif renderFlag == "yaml":
            print matches.yaml()
        elif renderFlag == "md":
            print matches.markdown()
        elif renderFlag == "table":
            print matches.markdown()
        elif renderFlag == "mysql":
            print matches.mysql(tableName=resultsTable)

    if level:
        from HMpTy import HTM
        mesh = HTM(
            depth=int(level),
            log=log
        )

        htmids = mesh.lookup_id(ra, dec)
        print htmids[0]

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
