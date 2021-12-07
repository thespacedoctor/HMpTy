#!/usr/bin/env python
# encoding: utf-8
"""
Documentation for HMpTy can be found here: http://HMpTy.readthedocs.org

Usage:
    hmpty init
    hmpty htmid <level> -- <ra> <dec>
    hmpty [-f] index <tableName> <primaryIdCol> <raCol> <decCol> (-s <pathToSettingsFile>|--host <host> --user <user> --passwd <passwd> --dbName <dbName>)
    hmpty search <tableName> <raCol> <decCol> <ra> <dec> <radius> (-s <pathToSettingsFile>|--host <host> --user <user> --passwd <passwd> --dbName <dbName>) [(-r <format>|-r mysql <resultsTable>)]

Options:
    init                  setup the sherlock settings file for the first time
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
from __future__ import print_function
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from subprocess import Popen, PIPE, STDOUT
from HMpTy.mysql import add_htm_ids_to_mysql_database_table, conesearch


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when `cl_utils.py` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False,
        projectName="HMpTy",
        defaultSettingsFile=True
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

    # UNPACK REMAINING CL ARGUMENTS USING `EXEC` TO SETUP THE VARIABLE NAMES
    # AUTOMATICALLY
    a = {}
    for arg, val in list(arguments.items()):
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        a[varname] = val
        if arg == "--dbConn":
            dbConn = val
            a["dbConn"] = val
        log.debug('%s = %s' % (varname, val,))

    hostFlag = a["hostFlag"]
    userFlag = a["userFlag"]
    passwdFlag = a["passwdFlag"]
    dbNameFlag = a["dbNameFlag"]
    tableName = a["tableName"]
    index = a["index"]
    htmid = a["htmid"]
    primaryIdCol = a["primaryIdCol"]
    raCol = a["raCol"]
    decCol = a["decCol"]
    ra = a["ra"]
    dec = a["dec"]
    radius = a["radius"]
    level = a["level"]
    forceFlag = a["forceFlag"]
    renderFlag = a["renderFlag"]
    search = a["search"]

    if "database settings" in settings:
        dbSettings = settings["database settings"]
    else:
        dbSettings = False

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    # set options interactively if user requests
    if "interactiveFlag" in a and a["interactiveFlag"]:

        # load previous settings
        moduleDirectory = os.path.dirname(__file__) + "/resources"
        pathToPickleFile = "%(moduleDirectory)s/previousSettings.p" % locals()
        try:
            with open(pathToPickleFile):
                pass
            previousSettingsExist = True
        except:
            previousSettingsExist = False
        previousSettings = {}
        if previousSettingsExist:
            previousSettings = pickle.load(open(pathToPickleFile, "rb"))

        # x-raw-input
        # x-boolean-raw-input
        # x-raw-input-with-default-value-from-previous-settings

        # save the most recently used requests
        pickleMeObjects = []
        pickleMe = {}
        theseLocals = locals()
        for k in pickleMeObjects:
            pickleMe[k] = theseLocals[k]
        pickle.dump(pickleMe, open(pathToPickleFile, "wb"))

    if a["init"]:
        from os.path import expanduser
        home = expanduser("~")
        filepath = home + "/.config/HMpTy/HMpTy.yaml"
        try:
            cmd = """open %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        try:
            cmd = """start %(filepath)s""" % locals()
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except:
            pass
        return

    # CALL FUNCTIONS/OBJECTS
    if index:
        add_htm_ids_to_mysql_database_table(
            raColName=raCol,
            declColName=decCol,
            tableName=tableName,
            dbConn=dbConn,
            log=log,
            primaryIdColumnName=primaryIdCol,
            reindex=forceFlag,
            dbSettings=dbSettings
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
            print(matches.table())
        elif renderFlag == "json":
            print(matches.json())
        elif renderFlag == "csv":
            print(matches.csv())
        elif renderFlag == "yaml":
            print(matches.yaml())
        elif renderFlag == "md":
            print(matches.markdown())
        elif renderFlag == "table":
            print(matches.markdown())
        elif renderFlag == "mysql":
            print(matches.mysql(tableName=resultsTable))

    if level:
        from HMpTy import HTM
        mesh = HTM(
            depth=int(level),
            log=log
        )

        htmids = mesh.lookup_id(ra, dec)
        print(htmids[0])

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
