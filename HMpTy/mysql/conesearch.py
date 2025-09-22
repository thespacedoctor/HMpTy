#!/usr/local/bin/python
# encoding: utf-8
"""
*Perform a conesearch on a database table with existing HTMId columns pre-populated*

:Author:
    David Young
"""
from __future__ import print_function
from __future__ import division
from future import standard_library
import copy
from io import StringIO
from fundamentals.mysql import readquery
import numpy as np
from HMpTy.htm import HTM
from fundamentals import tools
import re
import os
import sys
from past.utils import old_div
from builtins import object
from builtins import map
from builtins import str
from builtins import zip
standard_library.install_aliases()
os.environ['TERM'] = 'vt100'


class conesearch(object):
    """
    *The worker class for the conesearch module*

    **Key Arguments**

    - ``log`` -- logger
    - ``dbConn`` -- a database connection
    - ``tableName`` -- the name of the database table to perform the conesearch on.
    - ``columns`` -- the columns requested from the database table
    - ``ra`` -- the right ascension of the conesearch centre, can be single value or list of values
    - ``dec`` -- the declination of the conesearch centre, can be single value or list of values
    - ``radiusArcsec`` -- radius of the conesearch to be performed in arcsec
    - ``sqlWhere`` -- clause to add after "where" in the initial sql query of the conesearch. Default *False*
    - ``raCol`` -- the database table ra column name. Default * raDeg*
    - ``decCol`` -- the database table dec column name. Default *decDeg*
    - ``htmColumns`` -- the available HTM columns. Default *[10,13,16]*
    - ``separations`` -- include the separations in the final output. Default *False*
    - ``distinct`` -- request distinct columns from the database table (i.e. *select DISTINCT ...*). Default *False*
    - ``closest`` -- return the closest match only. Default *False*

    **Usage**

    Say we have 5 locations we wish to search a database table called *transientBucket* to see if it contains sources at those locations. Add the coordinates to those locations to RA and DEC lists like so:

    ```python
    raList = ["23:25:53.56",  "02:10:08.16",
           "13:20:00.00", 1.47329, 35.34279]
    decList = ["+26:54:23.9",  "-48:38:24.3",
            "+24:18:00.00",  8.43016, -42.34428]
    ```

    Note coordinates can be in decimal degrees or sexagesimal format (or both).

    To initialise a 10 arcsec conesearch to return the *transientBucketId* and *spectralType* values from any resulting match use the code:

    ```python
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
    ```

    Using the ``query`` property of the coneseach object you can inspect the initial sql query to be run on the database:

    ```python
    print(cs.query)
    ```

    ```text
    select transientBucketId, spectralType, raDeg, decDeg from transientBucket where htm16ID in (51985593986,51985593989,51985593993,51985593994,51985593995,51985593996,51985593997,51985593998,51985593999,51985594037, ... ,38488627914,38488627916,38488627918,38488627919,38488627956,38488627957,38488627959)
    ```

    To execute the query and return the results:

    ```python
    matchIndies, matches = cs.search()
    ```

    The ``matchIndies`` are the indices of the coordinate in the original ``raList`` and ``decList`` lists and the ``matches`` the matched rows from the database table.

    To constrain your results a little more define the ``distinct`` and or ``sqlWhere`` attributes of the conesearch:

    ```python
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
        sqlWhere="spectralType is not null",
        htmColumns=["htm10ID", "htm13ID", "htm16ID"]
    )


        matchIndies, matches = cs.search()

        for row in matches.list:
            print(row)
        ```

        ```text
        {'raDeg': 351.473208333, 'cmSepArcsec': 0.13379807128325164, 'decDeg': 26.9066388889, 'spectralType': u'SN Ia', 'transientBucketId': 1375799L}
        {'raDeg': 32.534, 'cmSepArcsec': 0.031941633602975743, 'decDeg': -48.6400888889, 'spectralType': u'II', 'transientBucketId': 1328883L}
        {'raDeg': 1.47329166667, 'cmSepArcsec': 0.0068727452774991196, 'decDeg': 8.43016111111, 'spectralType': u'SN Ia', 'transientBucketId': 1321322L}
        {'raDeg': 35.3427916667, 'cmSepArcsec': 0.0043467057710126393, 'decDeg': -42.3442805556, 'spectralType': u'Ia', 'transientBucketId': 1307226L}
        ```

        Note that by adding ``separations=True`` the matched source seperations from the original coordinate lists have been injected into the results.

        It is possible to render the results in csv, json, markdown, yaml or ascii table format. For example:

        ```python
        print(matches.table())
        ```

        ```text
        +-----------+---------------+-----------+--------------+--------------------+
        | raDeg     | spectralType  | decDeg    | cmSepArcsec  | transientBucketId  |
        +-----------+---------------+-----------+--------------+--------------------+
        | 351.4732  | SN Ia         | 26.9066   | 0.1338       | 1375799            |
        | 32.5340   | II            | -48.6401  | 0.0319       | 1328883            |
        | 1.4733    | SN Ia         | 8.4302    | 0.0069       | 1321322            |
        | 35.3428   | Ia            | -42.3443  | 0.0043       | 1307226            |
        +-----------+---------------+-----------+--------------+--------------------+
        ```

        To save the results to file:

        ```python
        matches.table(filepath="/path/to/my/results.dat")
        ```

        To instead render as csv, json, markdown or yaml use:

        ```python
        matches.csv(filepath="/path/to/my/results.csv")
        matches.json(filepath="/path/to/my/results.json")
        matches.markdown(filepath="/path/to/my/results.md")
        matches.markdown(filepath="/path/to/my/results.yaml")
        ```

        Finally, to render the results as mysql inserts, use the following code:

        ```python
        matches.mysql(tableName="mysql_table", filepath=None, createStatement=False)
        ```

        ```text
        INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.133798071283" ,"26.9066388889" ,"351.473208333" ,"SN Ia" ,"1375799")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.133798071283", decDeg="26.9066388889", raDeg="351.473208333", spectralType="SN Ia", transientBucketId="1375799", updated=IF( cmSepArcsec="0.133798071283" AND  decDeg="26.9066388889" AND  raDeg="351.473208333" AND  spectralType="SN Ia" AND  transientBucketId="1375799", 0, 1), dateLastModified=IF( cmSepArcsec="0.133798071283" AND  decDeg="26.9066388889" AND  raDeg="351.473208333" AND  spectralType="SN Ia" AND  transientBucketId="1375799", dateLastModified, NOW()) ;
        INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.031941633603" ,"-48.6400888889" ,"32.534" ,"II" ,"1328883")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.031941633603", decDeg="-48.6400888889", raDeg="32.534", spectralType="II", transientBucketId="1328883", updated=IF( cmSepArcsec="0.031941633603" AND  decDeg="-48.6400888889" AND  raDeg="32.534" AND  spectralType="II" AND  transientBucketId="1328883", 0, 1), dateLastModified=IF( cmSepArcsec="0.031941633603" AND  decDeg="-48.6400888889" AND  raDeg="32.534" AND  spectralType="II" AND  transientBucketId="1328883", dateLastModified, NOW()) ;
        INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.0068727452775" ,"8.43016111111" ,"1.47329166667" ,"SN Ia" ,"1321322")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.0068727452775", decDeg="8.43016111111", raDeg="1.47329166667", spectralType="SN Ia", transientBucketId="1321322", updated=IF( cmSepArcsec="0.0068727452775" AND  decDeg="8.43016111111" AND  raDeg="1.47329166667" AND  spectralType="SN Ia" AND  transientBucketId="1321322", 0, 1), dateLastModified=IF( cmSepArcsec="0.0068727452775" AND  decDeg="8.43016111111" AND  raDeg="1.47329166667" AND  spectralType="SN Ia" AND  transientBucketId="1321322", dateLastModified, NOW()) ;
        INSERT INTO `mysql_table` (cmSepArcsec,decDeg,raDeg,spectralType,transientBucketId) VALUES ("0.00434670577101" ,"-42.3442805556" ,"35.3427916667" ,"Ia" ,"1307226")  ON DUPLICATE KEY UPDATE  cmSepArcsec="0.00434670577101", decDeg="-42.3442805556", raDeg="35.3427916667", spectralType="Ia", transientBucketId="1307226", updated=IF( cmSepArcsec="0.00434670577101" AND  decDeg="-42.3442805556" AND  raDeg="35.3427916667" AND  spectralType="Ia" AND  transientBucketId="1307226", 0, 1), dateLastModified=IF( cmSepArcsec="0.00434670577101" AND  decDeg="-42.3442805556" AND  raDeg="35.3427916667" AND  spectralType="Ia" AND  transientBucketId="1307226", dateLastModified, NOW()) ;
        ```
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
            closest=False,
            htmColumns=["htm10ID", "htm13ID", "htm16ID"]
    ):
        self.log = log
        log.debug("instansiating a new 'conesearch' object")
        self.tableName = tableName
        self.dbConn = dbConn
        self.radius = float(radiusArcsec)
        self.raCol = raCol
        self.decCol = decCol
        self.columns = columns
        self.separations = separations
        self.distinct = distinct
        self.sqlWhere = sqlWhere
        self.closest = closest
        self.htmColumns = htmColumns

        if isinstance(self.htmColumns, int):
            self.htmColumns = [self.htmColumns]
        if isinstance(self.htmColumns, str):
            self.htmColumns = [self.htmColumns]

        import re

        self.htmColumnLevels = [int(re.search(r'\d+', i).group())
                                for i in self.htmColumns]

        for i in self.htmColumnLevels:
            if i not in [7, 10, 13, 16]:
                self.log.error(
                    f"htmColumns must be in the levels 7, 10, 13 and/or 16. The provided levels in this instance where {htmColumns}")
                raise AttributeError(
                    f"htmColumns must be in the levels 7, 10, 13 and/or 16. The provided levels in this instance where {htmColumns}")

        if not self.columns:
            self.columns = "*"

        # xt-self-arg-tmpx

        # BULK COORDINATE INTO NUMPY ARRAY
        from astrocalc.coords import coordinates_to_array
        self.ra, self.dec = coordinates_to_array(
            log=self.log,
            ra=ra,
            dec=dec
        )

        self.htmDepth = min(self.htmColumnLevels)

        # SETUP THE MESH
        # LESS THAN 10 ARCSEC (side 16 = 6 arcsec)
        if self.radius < 10. and 16 in self.htmColumnLevels:
            self.htmDepth = 16
        # LESS THAN 1 ARCMIN (side 13 = 48 arcsec)
        elif self.radius / 60 < 1. and 13 in self.htmColumnLevels:
            self.htmDepth = 13
        # LESS THAN 10 arcmin (side 10 = 6.4 arcmin)
        elif self.radius / 60 < 10. and 10 in self.htmColumnLevels:
            self.htmDepth = 10
        # GREATER THAN 0.5 DEG (side 7 = 0.8 DEG)
        elif 7 in self.htmColumnLevels:
            self.htmDepth = 7
        else:
            self.htmDepth = 10

        # SETUP A MESH AT CHOSEN DEPTH
        self.mesh = HTM(
            depth=self.htmDepth,
            log=self.log
        )

        # DATETIME REGEX - EXPENSIVE OPERATION, LET"S JUST DO IT ONCE
        self.reDatetime = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}T')

        return None

    @property
    def query(
            self):
        """*return the sql query for the HTM trixel search*

        **Usage**

        cs.query

        """
        return self._get_on_trixel_sources_from_database_query()

    def search(self):
        """
        *Return the results of the database conesearch*

        **Return**

        - ``conesearch``


        **Usage**

        See class usage.

        """
        self.log.debug('starting the ``get`` method')

        sqlQuery = self._get_on_trixel_sources_from_database_query()

        databaseRows = self._execute_query(sqlQuery)
        matchIndies, matches = self._list_crossmatch(databaseRows)

        from fundamentals.renderer import list_of_dictionaries
        matches = list_of_dictionaries(
            log=self.log,
            listOfDictionaries=matches,
            reDatetime=self.reDatetime
        )

        self.log.debug('completed the ``get`` method')
        return matchIndies, matches

    def _get_on_trixel_sources_from_database_query(
            self):
        """*generate the mysql query before executing it*
        """
        self.log.debug(
            'completed the ````_get_on_trixel_sources_from_database_query`` method')

        import numpy as np

        tableName = self.tableName
        raCol = self.raCol
        decCol = self.decCol
        radiusArc = self.radius
        radius = old_div(self.radius, (60. * 60.))

        # GET ALL THE TRIXELS REQUIRED
        trixelArray = self._get_trixel_ids_that_overlap_conesearch_circles()
        if trixelArray.size > 50000 and self.htmDepth >= 16 and 13 in self.htmColumnLevels:
            self.htmDepth = 13
            self.mesh = HTM(
                depth=self.htmDepth,
                log=self.log
            )
            trixelArray = self._get_trixel_ids_that_overlap_conesearch_circles()
        if trixelArray.size > 50000 and self.htmDepth >= 13 and 10 in self.htmColumnLevels:
            self.htmDepth = 10
            self.mesh = HTM(
                depth=self.htmDepth,
                log=self.log
            )
            trixelArray = self._get_trixel_ids_that_overlap_conesearch_circles()

        htmLevel = self.htmColumns[self.htmColumnLevels.index(self.htmDepth)]

        if trixelArray.size > 150000:
            self.log.info(
                "Your search radius of the `%(tableName)s` table may be too large (%(radiusArc)s arcsec)" % locals())
            minID = np.min(trixelArray)
            maxID = np.max(trixelArray)
            htmWhereClause = "where %(htmLevel)s between %(minID)s and %(maxID)s  " % locals(
            )
        else:
            thesHtmIds = ",".join(np.array(list(map(str, trixelArray))))
            htmWhereClause = "where %(htmLevel)s in (%(thesHtmIds)s)" % locals(
            )

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

        self.log.debug(
            'completed the ``_get_on_trixel_sources_from_database_query`` method')

        return sqlQuery

    def _get_trixel_ids_that_overlap_conesearch_circles(
            self):
        """*Get an array of all of the trixels IDs that overlap the conesearch circles(s)*

        **Return**

        - ``trixelArray`` -- an array of all the overlapping trixel ids

        """
        self.log.debug(
            'starting the ````_get_trixel_ids_that_overlap_conesearch_circles`` method')

        # CONVERT RADIUS TO DEGREES
        r = self.radius/(60. * 60.)

        # VECTORIZED COMPUTATION OF TRIXELS FOR ALL RA, DEC PAIRS
        trixelArray = np.concatenate([
            self.mesh.intersect(
                ra1, dec1, r, inclusive=True, convertCoordinates=False
            ) for ra1, dec1 in zip(self.ra, self.dec)
        ])

        # GET UNIQUE TRIXELS
        if trixelArray.size < 10000:
            trixelArray = np.array(list(set(trixelArray)))
        else:
            trixelArray = np.unique(trixelArray)

        self.log.debug(
            'completed the ``_get_trixel_ids_that_overlap_conesearch_circles`` method')
        return trixelArray

    def _execute_query(
            self,
            sqlQuery):
        """* execute query and trim results*

        **Key Arguments**

        - ``sqlQuery`` -- the sql database query to grab low-resolution results.


        **Return**

        - ``databaseRows`` -- the database rows found on HTM trixles with requested IDs

        """
        self.log.debug(
            'completed the ````_execute_query`` method')

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
            elif "Truncated incorrect DOUBLE value" in str(e) or "Truncated incorrect DECIMAL value" in str(e):
                databaseRows = readquery(
                    log=self.log,
                    sqlQuery=sqlQuery,
                    dbConn=self.dbConn,
                    quiet=True
                )
            else:
                print(sqlQuery)
                raise e

        if self.distinct and (self.columns != "*" and (self.raCol.lower() not in self.columns.lower() or self.decCol.lower() not in self.columns.lower())):
            distinctRows = []
            theseKeys = []
            for r in databaseRows:
                constraintKey = ""
                for k, v in list(r.items()):
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

        self.log.debug(
            'completed the ``_execute_query`` method')
        return databaseRows

    def _list_crossmatch(
            self,
            dbRows):
        """*to a finer grain crossmatch of the input coordinates and the database results.*

        **Key Arguments**

        - ``dbRows`` -- the rows return from the database on first crossmatch pass.


        **Return**

        - ``matchIndices1`` -- indices of the coordinate in the original ra and dec lists
        - ``matches`` -- the matched database rows

        """
        self.log.debug('starting the ``_list_crossmatch`` method')

        import time

        dbRas = []
        dbRas[:] = [d[self.raCol] for d in dbRows]
        dbDecs = []
        dbDecs[:] = [d[self.decCol] for d in dbRows]

        # 7 SEEMS TO BE GIVING OPTIMAL SPEED FOR MATCHES (VERY ROUGH SPEED
        # TESTS)
        mesh = HTM(
            depth=7,
            log=self.log
        )

        if self.closest:
            maxmatch = 1
        else:
            maxmatch = 0

        start_time = time.time()
        matchIndices1, matchIndices2, seps = mesh.match(
            ra1=self.ra,
            dec1=self.dec,
            ra2=np.array(dbRas),
            dec2=np.array(dbDecs),
            radius=float(self.radius/(60. * 60.)),
            maxmatch=maxmatch  # 1 = match closest 1, 0 = match all
        )
        end_time = time.time()

        matches = []

        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):

            if self.separations:

                dbRows[m2]["cmSepArcsec"] = s * (60. * 60.)
            # DEEPCOPY NEEDED IF SAME ELEMENT MATCHED BY 2 SEPERATE
            # ITEMS IN FIRST LIST
            matches.append(copy.deepcopy(dbRows[m2]))

        self.log.debug('completed the ``_list_crossmatch`` method')
        return matchIndices1, matches

    # xt-class-method
