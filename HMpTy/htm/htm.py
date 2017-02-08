#!/usr/local/bin/python
# encoding: utf-8
"""
*Tools for working with Hierarchical Triangular Meshes, including coordinate crossmatching*

:Author:
    David Young (originally forked from Erin Sheldon's esutil - esheldon)

:Date Created:
    October  6, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from astrocalc.coords import unit_conversion
import _htmcCode
import numpy
from sys import stdout


class HTM(_htmcCode.HTMC):
    """
    *A Hierarchical Triangular Mesh object*

    **Key Arguments:**
        - ``depth`` -- the depth of the mesh you wish to create. Default *16*

    **Usage:**

        To generate a mesh object:

        .. code-block:: python

            from HMpTy import HTM
            mesh16 = HTM(
                depth=16
            )
    """

    @property
    def depth(
            self):
        """*the depth of the HTM tree*

        **Usage:**

            .. code-block:: python

                mesh.depth
        """
        return super(HTM, self).depth()

    @property
    def area(
            self):
        """*The mean area of triangles in this mesh in units of square degrees.*

        **Usage:**

            .. code-block:: python

                mesh.area
        """
        pi = numpy.pi
        area0 = 4.0 * pi / 8.0
        areadiv = 4.0 ** self.depth
        area = area0 / areadiv * (180.0 / pi) ** 2
        return area

    def lookup_id(
            self,
            ra,
            dec):
        """*Lookup the ID of HTM trixel that a coordinate or lists of coordinates lie on*

        **Key Arguments:**
            - ``ra`` -- list, numpy array or single ra value (first coordinate set)
            - ``dec`` -- list, numpy array or single dec value (first coordinate set - must match ra1 array length)

        **Return:**
            - ``htmIds`` -- a list of HTM trixel ids the coordinates lie on

        **Usage:**

            To find the trixel IDs that a set of coordinate lie on:

            .. code-block:: python

                raList1 = ["13:20:00.00", 200.0, "13:20:00.00", 175.23, 21.36]
                decList1 = ["+24:18:00.00",  24.3,  "+24:18:00.00",  -28.25, -15.32]

                htmids = mesh.lookup_id(raList1, decList1)
                for h, r, d in zip(htmids, raList1, decList1):
                    print r, d, " --> ", h

        """
        self.log.info('starting the ``lookup_id`` method')

        from astrocalc.coords import coordinates_to_array
        raArray, decArray = coordinates_to_array(
            log=self.log,
            ra=ra,
            dec=dec
        )

        self.log.info('completed the ``lookup_id`` method')
        return super(HTM, self).lookup_id(raArray, decArray)

    # use the tab-trigger below for new method
    # xt-class-method

    def intersect(self, ra, dec, radius, inclusive=True, convertCoordinates=True):
        """*return IDs of all triangles contained within and/or intersecting a circle centered on a given ra and dec*

        **Key Arguments:**
            - ``ra`` -- RA of central point in decimal degrees or sexagesimal
            - ``dec`` -- DEC of central point in decimal degrees or sexagesimal
            - ``radius`` -- radius of circle in degrees
            - ``inclusive`` -- include IDs of triangles that intersect the circle as well as those completely inclosed by the circle. Default *True*
            - ``convertCoordinates`` -- convert the corrdinates passed to intersect. Default *True*
            -

        **Return:**
            - ``trixelArray`` -- a numpy array of the match trixel IDs

        **Usage:**

            To return the trixels overlapping a circle with a 10 arcsec radius centred at 23:25:53.56, +26:54:23.9

            .. code-block:: python

                overlappingTrixels = mesh16.intersect(
                    ra="23:25:53.56",
                    dec="+26:54:23.9",
                    radius=10 / (60 * 60),
                    inclusive=True
                )

            Or to return the trixels completing enclosed by a circle with a 1 degree radius centred at 23:25:53.56, +26:54:23.9

            .. code-block:: python

                overlappingTrixels = mesh16.intersect(
                    ra="23:25:53.56",
                    dec="+26:54:23.9",
                    radius=1,
                    inclusive=False
                )
        """
        # CONVERT RA AND DEC DECIMAL DEGREES

        if convertCoordinates == True:
            converter = unit_conversion(
                log=self.log
            )
            ra = converter.ra_sexegesimal_to_decimal(
                ra=ra
            )
            dec = converter.dec_sexegesimal_to_decimal(
                dec=dec
            )

        if inclusive:
            inc = 1
        else:
            inc = 0
        return super(HTM, self).intersect(ra, dec, radius, inc)

    def match(self, ra1, dec1, ra2, dec2, radius, maxmatch=1, convertToArray=True):
        """*Crossmatch two lists of ra/dec points*

        This is very efficient for large search angles and large lists. Note, if you need to match against the same points many times, you should use a `Matcher` object

        **Key Arguments:**
            - ``ra1`` -- list, numpy array or single ra value (first coordinate set)
            - ``dec1`` -- list, numpy array or single dec value (first coordinate set - must match ra1 array length)
            - ``ra2`` -- list, numpy array or single ra value (second coordinate set)
            - ``dec2`` -- list, numpy array or single dec value (second coordinate set - must match ra2 array length)
            - ``radius`` -- search radius in degrees. Can be list, numpy array or single value. If list or numpy array must be same length as ra1 array length)
            - ``maxmatch`` -- maximum number of matches to return. Set to `0` to match all points. Default *1* (i.e. closest match)
            - ``convertToArray`` -- convert the coordinates into an array. Default *True*. Can bypass the conversion check if you are sure coordinates in numpy array

        **Return:**
            - ``matchIndices1`` -- match indices for list1 (ra1, dec1)
            - ``matchIndices2`` -- match indices for list2 (ra2, dec2)
            - ``sepDeg`` -- separations between matched corrdinates in degrees. All returned arrays are the same size


        **Usage:**

            To match 2 lists of corrdinates try something like this:

            .. code-block:: python

                twoArcsec = 2.0 / 3600.
                raList1 = [200.0, 200.0, 200.0, 175.23, 21.36]
                decList1 = [24.3,  24.3,  24.3,  -28.25, -15.32]
                raList2 = [200.0, 200.0, 200.0, 175.23, 55.25]
                decList2 = [24.3 + 0.75 * twoArcsec, 24.3 + 0.25 * twoArcsec,
                            24.3 - 0.33 * twoArcsec, -28.25 + 0.58 * twoArcsec, 75.22]
                matchIndices1, matchIndices2, seps = mesh.match(
                    ra1=raList1,
                    dec1=decList1,
                    ra2=raList2,
                    dec2=decList2,
                    radius=twoArcsec,
                    maxmatch=0
                )

                for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
                    print raList1[m1], decList1[m1], " -> ", s * 3600., " arcsec -> ", raList2[m2], decList2[m2]

            Note from the print statement, you can index the arrays ``raList1``, ``decList1`` with the ``matchIndices1`` array values and  ``raList2``, ``decList2`` with the ``matchIndices2`` values.
        """

        # CONVERT LISTS AND SINGLE VALUES TO ARRAYS OF FLOATS
        ra1 = numpy.array(ra1, dtype='f8', ndmin=1, copy=False)
        dec1 = numpy.array(dec1, dtype='f8', ndmin=1, copy=False)
        ra2 = numpy.array(ra2, dtype='f8', ndmin=1, copy=False)
        dec2 = numpy.array(dec2, dtype='f8', ndmin=1, copy=False)
        radius = numpy.array(radius, dtype='f8', ndmin=1, copy=False)

        # CHECK ARRAY SIZES MATCH
        if (ra1.size != dec1.size
                or ra2.size != ra2.size):
            stup = (ra1.size, dec1.size, ra2.size, dec2.size)
            raise ValueError("ra1 must equal dec1 in size "
                             "and ra2 must equal dec2 in size, "
                             "got %d,%d and %d,%d" % stup)

        if radius.size != 1 and radius.size != ra2.size:
            raise ValueError("radius size (%d) != 1 and"
                             " != ra2,dec2 size (%d)" % (radius.size, ra2.size))

        # new way using a Matcher
        depth = self.depth
        matcher = Matcher(
            log=self.log,
            depth=depth,
            ra=ra2,
            dec=dec2,
            convertToArray=convertToArray)
        return matcher.match(
            ra=ra1,
            dec=dec1,
            radius=radius,
            maxmatch=maxmatch)


class Matcher(_htmcCode.Matcher):
    """*A matcher-array object to match other arrays of ra,dec against*

    The Matcher object is initialized with a set of ra,dec coordinates and can then be used and reused to match against other sets of coordinates

    **Key Arguments:**
        - ``log`` -- logger
        - ``depth`` -- the depth of the mesh generate the Matcher object at. Default *16*
        - ``ra`` -- list, numpy array or single ra value
        - ``dec`` -- --list, numpy array or single dec value (must match ra array length)
        - ``convertToArray`` -- convert the coordinates into an array. Default *True*. Can bypass the conversion check if you are sure coordinates in numpy array

    **Return:**
        - None

    **Usage:**

        If we have a set of coordinates such that:

        .. code-block:: python

            raList1 = [200.0, 200.0, 200.0, 175.23, 21.36]
            decList1 = [24.3,  24.3,  24.3,  -28.25, -15.32]

        We can initialise a matcher object like so:

        .. code-block:: python

            from HMpTy import Matcher
            coordinateSet = Matcher(
                log=log,
                ra=raList1,
                dec=decList1,
                depth=16
            )
    """

    def __init__(
            self,
            ra,
            dec,
            depth=16,
            log=False,
            convertToArray=True):

        self.convertToArray = convertToArray

        if log == False:
            if log == False:
                from fundamentals.logs import emptyLogger
                self.log = emptyLogger()
        else:
            self.log = log

        if convertToArray == True:
            from astrocalc.coords import coordinates_to_array
            ra, dec = coordinates_to_array(
                log=log,
                ra=ra,
                dec=dec
            )

        if ra.size != dec.size:
            raise ValueError("ra size (%d) != "
                             "dec size (%d)" % (ra.size, dec.size))

        super(Matcher, self).__init__(depth, ra, dec)

    @property
    def depth(
            self):
        """*the depth of the Matcher object*

        **Usage:**

            .. code-block:: python

                coordinateSet.depth
        """
        return super(Matcher, self).depth

    def match(self, ra, dec, radius, maxmatch=1):
        """*match a corrdinate set against this Matcher object's coordinate set*

        **Key Arguments:**
            - ``ra`` -- list, numpy array or single ra value
            - ``dec`` -- --list, numpy array or single dec value (must match ra array length)
            - ``radius`` -- radius of circle in degrees
            - ``maxmatch`` -- maximum number of matches to return. Set to `0` to match all points. Default *1* (i.e. closest match)

        **Return:**
            - None

        **Usage:**

            Once we have initialised a Matcher coordinateSet object we can match other coordinate sets against it:

            .. code-block:: python

                twoArcsec = 2.0 / 3600.
                raList2 = [200.0, 200.0, 200.0, 175.23, 55.25]
                decList2 = [24.3 + 0.75 * twoArcsec, 24.3 + 0.25 * twoArcsec,
                    24.3 - 0.33 * twoArcsec, -28.25 + 0.58 * twoArcsec, 75.22]

                matchIndices1, matchIndices2, seps = coordinateSet.match(
                    ra=raList2,
                    dec=decList2,
                    radius=twoArcsec,
                    maxmatch=0
                )

                for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
                    print raList1[m1], decList1[m1], " -> ", s * 3600., " arcsec -> ", raList2[m2], decList2[m2]

            Or to return just the nearest matches:

            .. code-block:: python

                matchIndices1, matchIndices2, seps = coordinateSet.match(
                    ra=raList2,
                    dec=decList2,
                    radius=twoArcsec,
                    maxmatch=1
                )

            Note from the print statement, you can index the arrays ``raList1``, ``decList1`` with the ``matchIndices1`` array values and  ``raList2``, ``decList2`` with the ``matchIndices2`` values.
        """

        if self.convertToArray == True:
            from astrocalc.coords import coordinates_to_array
            ra, dec = coordinates_to_array(
                log=self.log,
                ra=ra,
                dec=dec
            )

        radius = numpy.array(radius, dtype='f8', ndmin=1, copy=False)

        if ra.size != dec.size:
            raise ValueError("ra size (%d) != "
                             "dec size (%d)" % (ra.size, dec.size))

        if radius.size != 1 and radius.size != ra.size:
            raise ValueError("radius size (%d) != 1 and"
                             " != ra,dec size (%d)" % (radius.size, ra.size))

        return super(Matcher, self).match(ra, dec, radius, maxmatch, False)
