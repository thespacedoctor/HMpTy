#!/usr/local/bin/python
# encoding: utf-8
"""
*Perform a conesearch on a database table with existing HTMId columns pre-populated*

:Author:
    David Young

:Date Created:
    October  5, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from astrocalc.coords import unit_conversion, coordinates_to_array
from HMpTy.htm import HTM
import numpy as np
from fundamentals.mysql import readquery
from StringIO import StringIO


class conesearch():
    """
    *The worker class for the conesearch module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``dbConn`` -- a database connection
        - ``tableName`` -- the name of the database table to perform the conesearch on.
        - ``columns`` -- the columns requested from the database table
        - ``ra`` -- the right ascension of the conesearch centre, can be single value or list of values
        - ``dec`` -- the declination of the conesearch centre, can be single value or list of values
        - ``radiusArcsec`` -- radius of the conesearch to be performed in arcsecs
        - ``sqlWhere`` -- clause to add after "where" in the initial sql query of the conesearch. Default *False*
        - ``raCol`` -- the database table ra column name. Default * raDeg*
        - ``decCol`` -- the database table dec column name. Default *decDeg*
        - ``separations`` -- include the separations in the final output. Default *False*
        - ``distinct`` -- request distinct columns from the database table (i.e. *select DISTINCT ...*). Default *False*
        - ``closest`` -- return the closest match only. Default *False*

    **Usage:**

        Say we have 5 locations we wish to search a database table called *transientBucket* to see if it contains sources at those locations. Add the coordinates to those locations to RA and DEC lists like so:

        .. code-block:: python

            raList = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
            decList = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        Note coorinates can be in decimal degrees or sexegesimal format (or both).

        To initialise a 10 arcsec conesearch to return the *transientBucketId* and *spectralType* values from any resulting match use the code:

        .. code-block:: python

            from HMpTy.mysql import conesearch
            cs = conesearch(
                log=log,
                dbConn=dbConn,
                tableName="transientBucket",
                columns="transientBucketId, spectralType",
                ra=raList,
                dec=decList,
                radiusArcsec=10,
                separations=False,
                distinct=False,
                sqlWhere=False
            )

        Using the ``query`` property of the coneseach object you can inspect the initial sql query to be run on the database:

        .. code-block:: python

            print cs.query

        .. code-block:: text

            select transientBucketId, spectralType, raDeg, decDeg from transientBucket where htm16ID in (51985593986,51985593989,51985593993,51985593994,51985593995,51985593996,51985593997,51985593998,51985593999,51985594037, ... ,38488627914,38488627916,38488627918,38488627919,38488627956,38488627957,38488627959)

        To execute the query and return the results:

        .. code-block:: python

            matchIndies, matches = cs.search()

        The ``matchIndies`` are the indices of the coordinate in the original ``raList`` and ``decList`` lists and the ``matches`` the matched rows from the database table.

        To constrain your results a little more define the ``distinct`` and or ``sqlWhere`` attributes of the conesearch:

        .. code-block:: python

            from HMpTy.mysql import conesearch
            cs = conesearch(
                log=log,
                dbConn=dbConn,
                tableName="transientBucket",
                columns="transientBucketId, spectralType",
                ra=raList1,
                dec=decList1,
                radiusArcsec=10,
                separations=True,
                distinct=True,
                sqlWhere="spectralType is not null"
            )
            matchIndies, matches = cs.search()

            for row in matches.list:
                print row

        .. code-block:: text

            {'raDeg': 351.473208333, 'cmSepArcsec': 0.13379807128325164, 'decDeg': 26.9066388889, 'spectralType': u'SN Ia', 'transientBucketId': 1375799L}
            {'raDeg': 32.534, 'cmSepArcsec': 0.031941633602975743, 'decDeg': -48.6400888889, 'spectralType': u'II', 'transientBucketId': 1328883L}
            {'raDeg': 1.47329166667, 'cmSepArcsec': 0.0068727452774991196, 'decDeg': 8.43016111111, 'spectralType': u'SN Ia', 'transientBucketId': 1321322L}
            {'raDeg': 35.3427916667, 'cmSepArcsec': 0.0043467057710126393, 'decDeg': -42.3442805556, 'spectralType': u'Ia', 'transientBucketId': 1307226L}

        Note that by adding ``separations=True`` the matched source seperations from the original coordinate lists have been injected into the results.

        It is possible to render the results in csv, json, markdown, yaml or ascii table format. For example:

        .. code-block:: python

            print matches.table()

        .. code-block:: text

            +-----------+---------------+-----------+--------------+--------------------+
            | raDeg     | spectralType  | decDeg    | cmSepArcsec  | transientBucketId  |
            +-----------+---------------+-----------+--------------+--------------------+
            | 351.4732  | SN Ia         | 26.9066   | 0.1338       | 1375799            |
            | 32.5340   | II            | -48.6401  | 0.0319       | 1328883            |
            | 1.4733    | SN Ia         | 8.4302    | 0.0069       | 1321322            |
            | 35.3428   | Ia            | -42.3443  | 0.0043       | 1307226            |
            +-----------+---------------+-----------+--------------+--------------------+

        To save the results to file:

        .. code-block:: python

            matches.table(filepath="/path/to/my/results.dat")

        To instead render as csv, json, markdown or yaml use:

        .. code-block:: python

            matches.csv(filepath="/path/to/my/results.csv")
            matches.json(filepath="/path/to/my/results.json")
            matches.markdown(filepath="/path/to/my/results.md")
            matches.markdown(filepath="/path/to/my/results.yaml")

        Finally, to render the results as mysql inserts, use the following code:

        .. code-block:: python

            matches.mysql(tableName="mysql_table", filepath=None, createStatement=False)

        .. code-block:: text

            INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.133798071283" ,"26.9066388889" ,"351.473208333" ,"SN Ia" ,"1375799")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.133798071283", decDeg="26.9066388889", raDeg="351.473208333", spectralType="SN Ia", transientBucketId="1375799", updated=IF( cmSepArcsec="0.133798071283" AND  decDeg="26.9066388889" AND  raDeg="351.473208333" AND  spectralType="SN Ia" AND  transientBucketId="1375799", 0, 1), dateLastModified=IF( cmSepArcsec="0.133798071283" AND  decDeg="26.9066388889" AND  raDeg="351.473208333" AND  spectralType="SN Ia" AND  transientBucketId="1375799", dateLastModified, NOW()) ;
            INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.031941633603" ,"-48.6400888889" ,"32.534" ,"II" ,"1328883")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.031941633603", decDeg="-48.6400888889", raDeg="32.534", spectralType="II", transientBucketId="1328883", updated=IF( cmSepArcsec="0.031941633603" AND  decDeg="-48.6400888889" AND  raDeg="32.534" AND  spectralType="II" AND  transientBucketId="1328883", 0, 1), dateLastModified=IF( cmSepArcsec="0.031941633603" AND  decDeg="-48.6400888889" AND  raDeg="32.534" AND  spectralType="II" AND  transientBucketId="1328883", dateLastModified, NOW()) ;
            INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.0068727452775" ,"8.43016111111" ,"1.47329166667" ,"SN Ia" ,"1321322")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.0068727452775", decDeg="8.43016111111", raDeg="1.47329166667", spectralType="SN Ia", transientBucketId="1321322", updated=IF( cmSepArcsec="0.0068727452775" AND  decDeg="8.43016111111" AND  raDeg="1.47329166667" AND  spectralType="SN Ia" AND  transientBucketId="1321322", 0, 1), dateLastModified=IF( cmSepArcsec="0.0068727452775" AND  decDeg="8.43016111111" AND  raDeg="1.47329166667" AND  spectralType="SN Ia" AND  transientBucketId="1321322", dateLastModified, NOW()) ;
            INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.00434670577101" ,"-42.3442805556" ,"35.3427916667" ,"Ia" ,"1307226")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.00434670577101", decDeg="-42.3442805556", raDeg="35.3427916667", spectralType="Ia", transientBucketId="1307226", updated=IF( cmSepArcsec="0.00434670577101" AND  decDeg="-42.3442805556" AND  raDeg="35.3427916667" AND  spectralType="Ia" AND  transientBucketId="1307226", 0, 1), dateLastModified=IF( cmSepArcsec="0.00434670577101" AND  decDeg="-42.3442805556" AND  raDeg="35.3427916667" AND  spectralType="Ia" AND  transientBucketId="1307226", dateLastModified, NOW()) ;
    """
    # Initialisation

    def __init__(
            self,
            log,
            dbConn,
            tableName,
            columns,
            ra,
            dec,
            radiusArcsec,
            sqlWhere=False,
            raCol="raDeg",
            decCol="decDeg",
            separations=False,
            distinct=False,
            closest=False
    ):
        self.log = log
        log.debug("instansiating a new 'conesearch' object")
        self.tableName = tableName
        self.dbConn = dbConn
        self.radius = radiusArcsec
        self.raCol = raCol
        self.decCol = decCol
        self.columns = columns
        self.separations = separations
        self.distinct = distinct
        self.sqlWhere = sqlWhere
        self.closest = closest

        if not self.columns:
            self.columns = "*"

        # xt-self-arg-tmpx

        # BULK COORDINATE INTO NUMPY ARRAY
        self.ra, self.dec = coordinates_to_array(
            log=self.log,
            ra=ra,
            dec=dec
        )

        # SETUP THE MESH
        # LESS THAN 1 ARCMIN
        if self.radius < 60.:
            self.htmDepth = 16
        # LESS THAN 1 DEG BUT GREATER THAN 1 ARCMIN
        elif self.radius / (60 * 60) < 1.:
            self.htmDepth = 13
        # GREATER THAN 1 DEGREE
        else:
            self.htmDepth = 10

        # SETUP A MESH AT CHOOSEN DEPTH
        self.mesh = HTM(
            depth=self.htmDepth,
            log=self.log
        )

        return None

    @property
    def query(
            self):
        """*return the sql query for the HTM trixel search*

        **Usage:**

            cs.query
        """
        return self._get_on_trixel_sources_from_database_query()

    def search(self):
        """
        *Return the results of the database conesearch*

        **Return:**
            - ``conesearch``

        **Usage:**

            See class usage.
        """
        self.log.info('starting the ``get`` method')

        sqlQuery = self._get_on_trixel_sources_from_database_query()
        databaseRows = self._execute_query(sqlQuery)
        matchIndies, matches = self._list_crossmatch(databaseRows)

        from fundamentals.renderer import list_of_dictionaries
        matches = list_of_dictionaries(
            log=self.log,
            listOfDictionaries=matches
        )

        self.log.info('completed the ``get`` method')
        return matchIndies, matches

    def _get_on_trixel_sources_from_database_query(
            self):
        """*generate the mysql query before executing it*
        """
        self.log.info(
            'starting the ``_get_on_trixel_sources_from_database_query`` method')

        tableName = self.tableName
        raCol = self.raCol
        decCol = self.decCol
        radius = self.radius / (60. * 60.)

        # GET ALL THE TRIXELS REQUIRED
        trixelArray = self._get_trixel_ids_that_overlap_conesearch_circles()

        thesHtmIds = ",".join(np.array(map(str, trixelArray)))
        htmLevel = "htm%sID" % self.htmDepth
        htmWhereClause = "where %(htmLevel)s in (%(thesHtmIds)s)" % locals()

        cols = self.columns[:]
        if cols != "*" and raCol.lower() not in cols.lower():
            cols += ", " + raCol
        if cols != "*" and decCol.lower() not in cols.lower():
            cols += ", " + decCol

        # FINALLY BUILD THE FULL QUERY
        if self.distinct:
            sqlQuery = """select DISTINCT %(cols)s from %(tableName)s %(htmWhereClause)s""" % locals(
            )
        else:
            sqlQuery = """select %(cols)s from %(tableName)s %(htmWhereClause)s""" % locals(
            )

        if self.sqlWhere and len(self.sqlWhere):
            sqlQuery += " and " + self.sqlWhere

        self.log.info(
            'completed the ``_get_on_trixel_sources_from_database_query`` method')
        return sqlQuery

    def _get_trixel_ids_that_overlap_conesearch_circles(
            self):
        """*Get an array of all of the trixels IDs that overlap the conesearch circles(s)*

        **Return:**
            - ``trixelArray`` -- an array of all the overlapping trixel ids
        """
        self.log.info(
            'starting the ``_get_trixel_ids_that_overlap_conesearch_circles`` method')

        trixelArray = np.array([], dtype='int16', ndmin=1, copy=False)
        # FOR EACH RA, DEC SET IN THE NUMPY ARRAY, COLLECT THE OVERLAPPING HTM
        # TRIXELS
        for ra1, dec1 in zip(self.ra, self.dec):
            thisArray = self.mesh.intersect(
                ra1, dec1, self.radius / (60. * 60.), inclusive=True)
            trixelArray = np.hstack((trixelArray, thisArray))

        self.log.info(
            'completed the ``_get_trixel_ids_that_overlap_conesearch_circles`` method')
        return trixelArray

    def _execute_query(
            self,
            sqlQuery):
        """* execute query and trim results*

        **Key Arguments:**
            - ``sqlQuery`` -- the sql database query to grab low-resolution results.

        **Return:**
            - ``databaseRows`` -- the database rows found on HTM trixles with requested IDs
        """
        self.log.info(
            'starting the ``_execute_query`` method')

        try:
            databaseRows = readquery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )
        except Exception as e:
            if "Unknown column 'htm" in str(e):
                message = "Please add and populate the HTM columns to this database table BEFORE running any conesearches. You can use HMpTy to do this: http://hmpty.readthedocs.io/en/stable/"
                self.log.error(message)
                raise IOError(message)
            else:
                raise e

        if self.distinct and (self.columns != "*" and (self.raCol.lower() not in self.columns.lower() or self.decCol.lower() not in self.columns.lower())):
            distinctRows = []
            theseKeys = []
            for r in databaseRows:
                constraintKey = ""
                for k, v in r.iteritems():
                    if k.lower() != self.raCol.lower() and k.lower() != self.decCol.lower():
                        constraintKey += str(v)
                if self.raCol.lower() in self.columns.lower():
                    constraintKey += str(databaseRows[self.raCol])
                if self.decCol.lower() in self.columns.lower():
                    constraintKey += str(databaseRows[self.decCol])
                if constraintKey not in theseKeys:
                    theseKeys.append(constraintKey)
                    distinctRows.append(r)
            databaseRows = distinctRows

        self.log.info(
            'completed the ``_execute_query`` method')
        return databaseRows

    def _list_crossmatch(
            self,
            dbRows):
        """*to a finer grain crossmatch of the input coordinates and the database results.*

        **Key Arguments:**
            - ``dbRows`` -- the rows return from the database on first crossmatch pass.

        **Return:**
            - ``matchIndices1`` -- indices of the coordinate in the original ra and dec lists
            - ``matches`` -- the matched database rows
        """
        self.log.info('starting the ``_list_crossmatch`` method')

        dbRas = []
        dbRas[:] = [d[self.raCol] for d in dbRows]
        dbDecs = []
        dbDecs[:] = [d[self.decCol] for d in dbRows]

        # 12 SEEMS TO BE GIVING OPTIMAL SPEED FOR MATCHES (VERY ROUGH SPEED
        # TESTS)
        mesh = HTM(
            depth=12,
            log=self.log
        )

        if self.closest:
            maxmatch = 1
        else:
            maxmatch = 0
        matchIndices1, matchIndices2, seps = mesh.match(
            ra1=self.ra,
            dec1=self.dec,
            ra2=np.array(dbRas),
            dec2=np.array(dbDecs),
            radius=float(self.radius / (60. * 60.)),
            maxmatch=maxmatch  # 1 = match closest 1, 0 = match all
        )

        matches = []

        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
            if self.separations:
                dbRows[m2]["cmSepArcsec"] = s * (60. * 60.)
            matches.append(dbRows[m2])

        self.log.info('completed the ``_list_crossmatch`` method')
        return matchIndices1, matches

    # xt-class-method
