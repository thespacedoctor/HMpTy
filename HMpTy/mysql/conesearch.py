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


class conesearch():
    """
    *The worker class for the conesearch module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``dbConn`` -- a database connection
        - ``ra`` -- the right ascension of the conesearch centre
        - ``dec`` -- the declination of the conesearch centre
        - ``radiusArcsec`` -- radius of the conesearch to be performed in arcsecs
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
            ra,
            dec,
            radiusArcsec,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'conesearch' object")
        self.settings = settings
        self.dbConn = dbConn
        self.radiusArcsec = radiusArcsec
        self.ra = ra
        self.dec = dec

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
        self.ra = converter.ra_sexegesimal_to_decimal(
            ra=self.ra
        )
        self.dec = converter.dec_sexegesimal_to_decimal(
            dec=self.dec
        )

        return None

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

        # BUILD WHERE SECTION OF CLAUSE
        self.radius = float(self.radius)
        htmWhereClause = htmCircle.htmCircleRegion(
            self.htmLevel, self.ra, self.dec, self.radius)

        # CONVERT RA AND DEC TO CARTESIAN COORDINATES
        ra = math.radians(self.ra)
        dec = math.radians(self.dec)
        cos_dec = math.cos(dec)
        cx = math.cos(ra) * cos_dec
        cy = math.sin(ra) * cos_dec
        cz = math.sin(dec)
        cartesians = (cx, cy, cz)

        # CREATE CARTESIAN SECTION OF QUERY
        cartesianClause = 'and (cx * %.17f + cy * %.17f + cz * %.17f >= cos(%.17f))' % (
            cartesians[0], cartesians[1], cartesians[2], math.radians(self.radius / 3600.0))

        # DECIDE WHAT COLUMNS TO REQUEST
        if self.queryType == 1:
            columns = self.quickColumns
        elif self.queryType == 3:
            columns = ['count(*) number']
        else:
            columns = ['*']

        columns = ','.join(columns)
        tableName = self.tableName

        # FINALLY BUILD THE FULL QUERY
        self.sqlQuery = "select %(columns)s from %(tableName)s %(htmWhereClause)s %(cartesianClause)s" % locals(
        )

        self.log.info('completed the ``generate_the_sql_query`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method
