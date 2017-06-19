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
import pymysql as ms
from fundamentals.mysql import readquery, writequery
from datetime import datetime, date
from fundamentals import times
import time


def add_htm_ids_to_mysql_database_table(
        raColName,
        declColName,
        tableName,
        dbConn,
        log,
        primaryIdColumnName="primaryId",
        cartesian=False,
        batchSize=25000,
        reindex=False):
    """*Given a database connection, a name of a table and the column names for RA and DEC, generates ID for one or more HTM level in the table*

    **Key Arguments:**
        - ``raColName`` -- ra in sexegesimal
        - ``declColName`` -- dec in sexegesimal
        - ``tableName`` -- name of table to add htmid info to
        - ``dbConn`` -- database hosting the above table
        - ``log`` -- logger
        - ``primaryIdColumnName`` -- the primary id for the table
        - ``cartesian`` -- add cartesian columns. Default *False*
        - ``batchSize`` -- the size of the batches of rows to add HTMIds to concurrently. Default *2500*
        - ``reindex`` -- reindex the entire table

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
                primaryIdColumnName="primaryId",
                reindex=False
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

    log.debug(
        """Checking the table %(tableName)s exists in the database""" % locals())
    tableList = []
    for row in rows:
        tableList.extend(row.values())
    if tableName not in tableList:
        message = "The %s table does not exist in the database" % (tableName,)
        log.critical(message)
        raise IOError(message)

    log.debug(
        """Checking the RA and DEC columns exist in the %(tableName)s table""" % locals())
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

    if cartesian:
        # ACTION(S) ##
        htmCols = {
            'htm16ID': 'BIGINT(20)',
            'htm13ID': 'INT',
            'htm10ID': 'INT',
            'cx': 'DOUBLE',
            'cy': 'DOUBLE',
            'cz': 'DOUBLE'
        }
    else:
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

    log.debug(
        """Counting the number of rows still requiring HTMID information""" % locals())
    if reindex:
        sqlQuery = u"""
            SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS
                WHERE table_schema=DATABASE() AND table_name='%(tableName)s' and COLUMN_NAME = "%(primaryIdColumnName)s";
        """ % locals()
        keyname = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=dbConn
        )[0]["INDEX_NAME"]
        if keyname != "PRIMARY":
            log.error('To reindex the entire table the primaryID you submit must be unique. "%(primaryIdColumnName)s" is not unique in table "%(tableName)s"' % locals())
            return

        sqlQuery = """ALTER TABLE `%(tableName)s` disable keys""" % locals()
        writequery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=dbConn
        )

        sqlQuery = """SELECT count(*) as count from `%(tableName)s`""" % locals(
        )
    elif cartesian:
        # COUNT ROWS WHERE HTMIDs ARE NOT SET
        sqlQuery = """SELECT count(*) as count from `%(tableName)s` where htm10ID is NULL or cx is null and %(raColName)s is not null""" % locals(
        )
    else:
        # COUNT ROWS WHERE HTMIDs ARE NOT SET
        sqlQuery = """SELECT count(*) as count from `%(tableName)s` where htm10ID is NULL and %(raColName)s is not null""" % locals(
        )
    log.debug(
        """SQLQUERY:\n\n%(sqlQuery)s\n\n""" % locals())
    rowCount = readquery(
        log=log,
        sqlQuery=sqlQuery,
        dbConn=dbConn,
        quiet=False
    )
    totalCount = rowCount[0]["count"]

    # ADD HTMIDs IN BATCHES
    total = totalCount
    batches = int(total / batchSize)

    count = 0
    lastId = False
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

        start = time.time()

        log.debug(
            """Selecting the next %(batchSize)s rows requiring HTMID information in the %(tableName)s table""" % locals())
        if reindex:
            # SELECT THE ROWS WHERE THE HTMIds ARE NOT SET
            if lastId:
                sqlQuery = """SELECT `%s`, `%s`, `%s` from `%s` where `%s` > '%s' order by `%s` limit %s""" % (
                    primaryIdColumnName, raColName, declColName, tableName, primaryIdColumnName,  lastId, primaryIdColumnName, batchSize)
            else:
                sqlQuery = """SELECT `%s`, `%s`, `%s` from `%s` order by `%s` limit %s""" % (
                    primaryIdColumnName, raColName, declColName, tableName, primaryIdColumnName, batchSize)
        elif cartesian:
            # SELECT THE ROWS WHERE THE HTMIds ARE NOT SET
            sqlQuery = """SELECT `%s`, `%s`, `%s` from `%s` where `%s` is not null and `%s` > 0 and ((htm10ID is NULL or cx is null)) limit %s""" % (
                primaryIdColumnName, raColName, declColName, tableName, raColName, raColName, batchSize)
        else:
            # SELECT THE ROWS WHERE THE HTMIds ARE NOT SET
            sqlQuery = """SELECT `%s`, `%s`, `%s` from `%s` where `%s` is not null and `%s` > 0 and htm10ID is NULL limit %s""" % (
                primaryIdColumnName, raColName, declColName, tableName, raColName, raColName, batchSize)
        batch = readquery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=dbConn
        )
        if reindex and len(batch):
            lastId = batch[-1][primaryIdColumnName]
        log.debug(
            """The next %(batchSize)s rows requiring HTMID information have now been selected""" % locals())

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

        log.debug(
            'calculating htmIds for batch of %s rows in %s db table' % (batchSize, tableName, ))
        htm16Ids = mesh16.lookup_id(raList, decList)
        htm13Ids = mesh13.lookup_id(raList, decList)
        htm10Ids = mesh10.lookup_id(raList, decList)
        log.debug(
            'finshed calculating htmIds for batch of %s rows in %s db table' % (batchSize, tableName, ))
        if cartesian:
            log.debug(
                'calculating cartesian coordinates for batch of %s rows in %s db table' % (batchSize, tableName, ))
            cx = []
            cy = []
            cz = []
            for r, d in zip(raList, decList):
                r = math.radians(r)
                d = math.radians(d)
                cos_dec = math.cos(d)
                cx.append(math.cos(r) * cos_dec)
                cy.append(math.sin(r) * cos_dec)
                cz.append(math.sin(d))

            sqlQuery = ""
            for h16, h13, h10, pid, cxx, cyy, czz in zip(htm16Ids, htm13Ids, htm10Ids, pIdList, cx, cy, cz):

                sqlQuery += \
                    """UPDATE `%s` SET htm16ID=%s, htm13ID=%s, htm10ID=%s, cx=%s, cy=%s, cz=%s where `%s` = '%s';\n""" \
                    % (
                        tableName,
                        h16,
                        h13,
                        h10,
                        cxx,
                        cyy,
                        czz,
                        primaryIdColumnName,
                        pid
                    )

            log.debug(
                'finished calculating cartesian coordinates for batch of %s rows in %s db table' % (
                    batchSize, tableName, ))
        else:
            log.debug('building the sqlquery')
            updates = []
            updates[:] = ["UPDATE `%(tableName)s` SET htm16ID=%(h16)s, htm13ID=%(h13)s, htm10ID=%(h10)s where %(primaryIdColumnName)s = '%(pid)s';" % locals() for h16,
                          h13, h10, pid in zip(htm16Ids, htm13Ids, htm10Ids, pIdList)]
            sqlQuery = "\n".join(updates)
            log.debug('finshed building the sqlquery')

        if len(sqlQuery):
            log.debug(
                'starting to update the HTMIds for new objects in the %s db table' % (tableName, ))
            writequery(
                log=log,
                sqlQuery=sqlQuery,
                dbConn=dbConn,
            )
            log.debug(
                'finished updating the HTMIds for new objects in the %s db table' % (tableName, ))
        else:
            log.debug(
                'no HTMIds to add to the %s db table' % (tableName, ))

        percent = float(count) * 100. / float(totalCount)
        print "%(count)s / %(totalCount)s htmIds added to %(tableName)s (%(percent)0.5f%% complete)" % locals()
        end = time.time()
        timediff = end - start
        timediff = timediff * 1000000. / float(batchSize)
        print "Update speed: %(timediff)0.2fs/1e6 rows\n" % locals()

    # APPLY INDEXES IF NEEDED
    sqlQuery = ""
    for index in ["htm10ID", "htm13ID", "htm16ID"]:
        log.debug('adding %(index)s index to %(tableName)s' % locals())
        iname = "idx_" + index
        asqlQuery = u"""
            SELECT COUNT(1) IndexIsThere FROM INFORMATION_SCHEMA.STATISTICS
                WHERE table_schema=DATABASE() AND table_name='%(tableName)s' AND index_name='%(iname)s';
        """ % locals()
        count = readquery(
            log=log,
            sqlQuery=asqlQuery,
            dbConn=dbConn
        )[0]["IndexIsThere"]

        if count == 0:
            if not len(sqlQuery):
                sqlQuery += u"""
                    ALTER TABLE %(tableName)s ADD INDEX `%(iname)s` (`%(index)s` ASC)
                """ % locals()
            else:
                sqlQuery += u""", ADD INDEX `%(iname)s` (`%(index)s` ASC)""" % locals()
    if len(sqlQuery):
        writequery(
            log=log,
            sqlQuery=sqlQuery + ";",
            dbConn=dbConn,
        )
    log.debug('finished adding indexes to %(tableName)s' % locals())

    if reindex:
        print "Re-enabling keys within the '%(tableName)s' table" % locals()
        sqlQuery = """ALTER TABLE `%(tableName)s` enable keys""" % locals()
        writequery(
            log=log,
            sqlQuery=sqlQuery,
            dbConn=dbConn
        )

    print "All HTMIds added to %(tableName)s" % locals()

    log.info('completed the ``add_htm_ids_to_mysql_database_table`` function')
    return None
