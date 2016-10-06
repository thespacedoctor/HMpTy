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
from astrocalc.coords import unit_conversion
from HMpTy import htm
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
        - ``idCol`` -- the object ID column of the database being searched 
        - ``ra`` -- the right ascension of the conesearch centre, can be single value or list of values
        - ``dec`` -- the declination of the conesearch centre, can be single value or list of values
        - ``radiusArcsec`` -- radius of the conesearch to be performed in arcsecs
        - ``raCol`` - - the ra column name of the database table being searched. Default * raDeg*
        - ``decCol`` -- the dec column name of the database table being searched. Default *decDeg*
        - ``settings`` -- the settings dictionary

    **Usage:**
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - update the package tutorial if needed

        .. code-block:: python 

            usage code   
    """
    # Initialisation

    def __init__(
            self,
            log,
            dbConn,
            tableName,
            idCol,
            ra,
            dec,
            radiusArcsec,
            raCol="raDeg",
            decCol="decDeg",
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'conesearch' object")
        self.settings = settings
        self.tableName = tableName
        self.dbConn = dbConn
        self.radius = radiusArcsec
        self.raCol = raCol
        self.decCol = decCol
        self.idCol = idCol

        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions
        # ASTROCALC UNIT CONVERTER OBJECT
        converter = unit_conversion(
            log=log
        )
        # CONVERT RA AND DEC TO NUMPY ARRAYS
        if isinstance(ra, str) or isinstance(ra, float):
            self.ra = np.array([converter.ra_sexegesimal_to_decimal(
                ra=ra
            )])
        elif isinstance(ra, list):
            raList = []
            raList[:] = [converter.ra_sexegesimal_to_decimal(ra=r) for r in ra]
            self.ra = np.array(raList)
        if isinstance(ra, str) or isinstance(ra, float):
            self.dec = np.array([converter.dec_sexegesimal_to_decimal(
                dec=dec
            )])
        elif isinstance(dec, list):
            decList = []
            decList[:] = [
                converter.dec_sexegesimal_to_decimal(dec=d) for d in dec]
            self.dec = np.array(decList)

        return None

    @property
    def query(
            self):
        """*return the sql query for the conesearch*

        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - update package usage if needed

            .. code-block:: python 

                usage code 
        """

        return self.generate_the_sql_query()

    # use the tab-trigger below for new property
    # xt-python-property

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def get(self):
        """
        *get the conesearch object*

        **Return:**
            - ``conesearch``

        **Usage:**
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - update the package tutorial if needed

        .. code-block:: python 

            usage code 
        """
        self.log.info('starting the ``get`` method')

        conesearch = None

        self.log.info('completed the ``get`` method')
        return conesearch

    def generate_the_sql_query(
            self):
        """*generate the mysql query before executing it*

        **Key Arguments:**
            # -

        **Return:**
            - None

        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - update package tutorial if needed

            .. code-block:: python 

                usage code 

        """
        self.log.info('starting the ``generate_the_sql_query`` method')

        tableName = self.tableName
        raCol = self.raCol
        decCol = self.decCol

        # CREATE AN ARRAY OF RELEVANT HTMIDS AND FIND MAX AND MIN
        mesh16 = htm.HTM(16)
        theseArrays = []
        radius = self.radius / (60. * 60.)

        ra = []
        dec = []
        # FOR EACH RA, DEC SET IN THE NUMPY ARRAY, COLLECT THE SOURCES FOUND IN
        # THE OVERLAPPING HTM TRIXELS FROM THE DATABASE
        for ra1, dec1 in zip(self.ra, self.dec):

            thisArray = mesh16.intersect(
                ra1, dec1, radius, inclusive=True)
            print list(thisArray)
            hmax = thisArray.max()
            hmin = thisArray.min()

            ratio = float(hmax - hmin + 1) / float(thisArray.size)
            if thisArray.size > 2000:
                htmWhereClause = "where htm16ID between %(hmin)s and %(hmax)s" % locals(
                )
            else:
                s = StringIO()
                np.savetxt(s, thisArray, fmt='%d', newline=",")
                thesHtmIds = s.getvalue()[:-1]
                htmWhereClause = "where htm16ID in (%(thesHtmIds)s)" % locals()

            # FINALLY BUILD THE FULL QUERY
            sqlQuery = """select %(raCol)s, %(decCol)s from %(tableName)s %(htmWhereClause)s""" % locals(
            )
            rows = readquery(
                log=self.log,
                sqlQuery=sqlQuery,
                dbConn=self.dbConn
            )

            # COLLECT THE RA AND DEC OF FIRST MATCH SOURCES
            raList = []
            raList[:] = [r[raCol] for r in rows]
            decList = []
            decList[:] = [r[decCol] for r in rows]
            tRa = np.array([ra1])
            tDec = np.array([dec1])
            raList = np.array(raList)
            decList = np.array(decList)

            # TRIM THE MATCHES TO THE EXACT AREA OF THE CONESEARCH AND
            # DETERMINE SEPARATIONS
            indexList1, indexList2, separation = mesh16.match(
                tRa, tDec, raList, decList, radius, maxmatch=0)
            for i in range(indexList1.size):
                ra.append(rows[indexList2[i]][raCol])
                dec.append(rows[indexList2[i]][decCol])

        ra = np.array(ra)
        dec = np.array(dec)

        self.log.info('completed the ``generate_the_sql_query`` method')
        return ra, dec

    # use the tab-trigger below for new method
    # xt-class-method
