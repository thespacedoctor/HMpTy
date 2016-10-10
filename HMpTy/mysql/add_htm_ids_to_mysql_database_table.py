#!/usr/local/bin/python
# encoding: utf-8
"""
*Given a database connection, a name of a table and the column names for RA and DEC, generates ID for one or more HTM level in the table*

:Author:
    David Young

:Date Created:
    June 21, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import math
os.environ['TERM'] = 'vt100'
from fundamentals import tools
import MySQLdb as ms
from fundamentals.mysql import readquery, writequery


def add_htm_ids_to_mysql_database_table(
        raColName,
        declColName,
        tableName,
        dbConn,
        log,
        primaryIdColumnName="primaryId"):
    """*Given a database connection, a name of a table and the column names for RA and DEC, generates ID for one or more HTM level in the table*

    **Key Arguments:**
        - ``raColName`` -- ra in sexegesimal
        - ``declColName`` -- dec in sexegesimal
        - ``tableName`` -- name of table to add htmid info to
        - ``dbConn`` -- database hosting the above table
        - ``log`` -- logger
        - ``primaryIdColumnName`` -- the primary id for the table

    **Return:**
        - None

    **Usage:**

        .. code-block:: python 

            from HMpTy.mysql import add_htm_ids_to_mysql_database_table
            add_htm_ids_to_mysql_database_table(
                raColName="raDeg",
                declColName="decDeg",
                tableName="my_big_star_table",
                dbConn=dbConn,
                log=log,
                primaryIdColumnName="primaryId"
            )
    """
    log.info('starting the ``add_htm_ids_to_mysql_database_table`` function')

    # TEST TABLE EXIST
    sqlQuery = """show tables"""
    rows = readquery(
        log=log,
        sqlQuery=sqlQuery,
        dbConn=dbConn
    )

    tableList = []
    for row in rows:
        tableList.extend(row.values())
    if tableName not in tableList:
        message = "The %s table does not exist in the database" % (tableName,)
        log.critical(message)
        raise IOError(message)

    # TEST COLUMNS EXISTS
    cursor = dbConn.cursor(ms.cursors.DictCursor)
    sqlQuery = """SELECT * FROM %s LIMIT 1""" % (tableName,)
    cursor.execute(sqlQuery)
    rows = cursor.fetchall()
    desc = cursor.description
    existingColumns = []
    for i in range(len(desc)):
        existingColumns.append(desc[i][0])
    if (raColName not in existingColumns) or (declColName not in existingColumns):
        message = 'Please make sure you have got the naes of the RA and DEC columns correct'
        log.critical(message)
        raise IOError(message)

    # ACTION(S) ##
    htmCols = {
        'htm16ID': 'BIGINT(20)',
        'htm13ID': 'INT',
        'htm10ID': 'INT'
    }

    # CHECK IF COLUMNS EXISTS YET - IF NOT CREATE FROM
    for key in htmCols.keys():
        try:
            log.debug(
                'attempting to check and generate the HTMId columns for the %s db table' %
                (tableName, ))
            colExists = \
                """SELECT *
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA=DATABASE()
                    AND COLUMN_NAME='%s'
                    AND TABLE_NAME='%s'""" \
                % (key, tableName)
            colExists = readquery(
                log=log,
                sqlQuery=colExists,
                dbConn=dbConn
            )
            switch = 0
            if not colExists:
                if switch == 0:
                    print "Adding the HTMCircle columns to %(tableName)s" % locals()
                    switch = 1
                sqlQuery = 'ALTER TABLE ' + tableName + ' ADD ' + \
                    key + ' ' + htmCols[key] + ' DEFAULT NULL'
                writequery(
                    log=log,
                    sqlQuery=sqlQuery,
                    dbConn=dbConn,
                )
        except Exception as e:
            log.critical('could not check and generate the HTMId columns for the %s db table - failed with this error: %s '
                         % (tableName, str(e)))
            raise e

    # COUNT ROWS WHERE HTMIDs ARE NOT SET
    sqlQuery = """SELECT count(*) as count from %(tableName)s where %(raColName)s is not null and  ((htm16ID is NULL or htm16ID = 0 or htm13ID is NULL or htm13ID = 0 or htm10ID is NULL or htm10ID = 0))""" % locals(
    )
    rowCount = readquery(
        log=log,
        sqlQuery=sqlQuery,
        dbConn=dbConn
    )
    totalCount = rowCount[0]["count"]

    # ADD HTMIDs IN BATCHES
    batchSize = 2500
    total = totalCount
    batches = int(total / batchSize)

    count = 0
    # NOW GENERATE THE HTMLIds FOR THESE ROWS
    for i in range(batches + 1):
        if total == 0:
            continue
        count += batchSize
        if count > batchSize:
            # Cursor up one line and clear line
            sys.stdout.write("\x1b[1A\x1b[2K")
        if count > totalCount:
            count = totalCount
        print "%(count)s / %(totalCount)s htmIds added to %(tableName)s" % locals()

        # SELECT THE ROWS WHERE THE HTMIds ARE NOT SET
        sqlQuery = """SELECT %s, %s, %s from %s where %s is not null and ((htm16ID is NULL or htm16ID = 0 or htm13ID is NULL or htm13ID = 0 or htm10ID is NULL or htm10ID = 0)) limit %s""" % (
            primaryIdColumnName, raColName, declColName, tableName, raColName, batchSize)
        batch = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=dbConn
        )

        raList = []
        decList = []
        pIdList = []
        raList[:] = [r[raColName] for r in batch]
        decList[:] = [r[declColName] for r in batch]
        pIdList[:] = [r[primaryIdColumnName] for r in batch]

        from HMpTy import htm
        mesh16 = htm.HTM(16)
        mesh13 = htm.HTM(13)
        mesh10 = htm.HTM(10)

        htm16Ids = mesh16.lookup_id(raList, decList)
        htm13Ids = mesh13.lookup_id(raList, decList)
        htm10Ids = mesh10.lookup_id(raList, decList)

        sqlQuery = ""
        for h16, h13, h10, pid in zip(htm16Ids, htm13Ids, htm10Ids, pIdList):

            sqlQuery += \
                """UPDATE %s SET htm16ID=%s, htm13ID=%s, htm10ID=%s where %s = '%s';\n""" \
                % (
                    tableName,
                    h16,
                    h13,
                    h10,
                    primaryIdColumnName,
                    pid
                )

        try:
            if len(sqlQuery):
                log.debug(
                    'attempting to update the HTMIds for new objects in the %s db table' % (tableName, ))
                writequery(
                    log=log,
                    sqlQuery=sqlQuery,
                    dbConn=dbConn,
                )
            else:
                log.debug(
                    'no HTMIds to add to the %s db table' % (tableName, ))
        except Exception as e:
            log.critical('could not update the HTMIds for new objects in the %s db table - failed with this error: %s '
                         % (tableName, str(e)))
            return -1

    # APPLY INDEXES IF NEEDED
    try:
        sqlQuery = u"""
            ALTER TABLE %(tableName)s  ADD INDEX `idx_htm10ID` (`htm13ID` ASC);
            ALTER TABLE %(tableName)s  ADD INDEX `idx_htm13ID` (`htm13ID` ASC);
            ALTER TABLE %(tableName)s  ADD INDEX `idx_htm16ID` (`htm16ID` ASC);
        """ % locals()
        writequery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=dbConn,
        )

    except Exception, e:
        log.info('no index needed on table: %(e)s' % locals())

    print "All HTMIds added to %(tableName)s" % locals()

    log.info('completed the ``add_htm_ids_to_mysql_database_table`` function')
    return None
