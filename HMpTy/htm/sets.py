#!/usr/local/bin/python
# encoding: utf-8
"""
*Given a list of coordinates and a crossmatch radius, split the list up into sets of associated locations*

:Author:
    David Young
"""
from line_profiler import profile
import numpy as np
from fundamentals import tools
from builtins import zip
from builtins import object
import sys
import os
os.environ['TERM'] = 'vt100'


class sets(object):
    """
    *Given a list of coordinates and a crossmatch radius, split the list up into sets of associated locations*

    **Key Arguments**

    - ``log`` -- logger
    - ``ra`` -- a list of the corrdinate right ascensions
    - ``dec`` -- a list of the corrdinate declinations (same length as ``ra``)
    - ``radius`` -- the radius to crossmatch the list of coordinates against itself (degrees)
    - ``sourceList`` -- the list of source imformation to be divided into associated sets (same length as ``ra`` and ``dec``)
    - ``convertToArray`` -- convert the coordinates into an array. Default *True*. Can bypass the conversion check if you are sure coordinates in numpy array


    **Usage**

    Given a list of transient metadata (any list, possibly a list of dictionaries) you can divide the list to assoicated sets of transients by running the following code:

    ```python
    from HMpTy.htm import sets
    xmatcher = sets(
        log=log,
        ra=raList,
        dec=decList,
        radius=10 / (60. * 60.),
        sourceList=transientList
    )
    allMatches = xmatcher.match 
    ```

    ``raList`` and ``decList`` are the coordinates for the sources found in the ``transientList`` and are therefore the same length as the `transientList`` (it's up to the user to create these lists). 
    This code will group the sources into set of assocated transients which are within a radius of 10 arcsecs from one-another. ``allMatches`` is a list of lists, each contained list being an associate group of sources.

    .. image:: https://i.imgur.com/hHExDqR.png
        :width: 800px
        :alt: divide a list of sources into associated sets

    """
    # Initialisation

    def __init__(
            self,
            log,
            ra,
            dec,
            radius,
            sourceList,
            convertToArray=True
    ):
        self.log = log
        log.debug("instansiating a new 'sets' object")
        self.ra = ra
        self.dec = dec
        self.radius = radius
        self.sourceList = sourceList
        self.convertToArray = convertToArray
        # Initial Actions

        if self.radius < 10.:
            self.htmDepth = 16
        # LESS THAN 1 ARCMIN (side 13 = 48 arcsec)
        elif self.radius / 60 < 1.:
            self.htmDepth = 13
        # LESS THAN 10 arcmin (side 10 = 6.4 arcmin)
        elif self.radius / 60 < 10.:
            self.htmDepth = 10
        # GREATER THAN 0.5 DEG (side 7 = 0.8 DEG)
        elif 7 in self.htmColumnLevels:
            self.htmDepth = 7

        from HMpTy import HTM
        self.mesh = HTM(
            depth=self.htmDepth,
            log=self.log
        )

        return None

    @property
    def match(
            self):
        """*all of the assocaited sets of sources*

        See the class for usage
        """

        return self._extract_all_sets_from_list()

    @profile
    def _extract_all_sets_from_list(
            self):
        """*Extract all of the sets from the list of coordinates*

        **Return**

        - ``allMatches`` -- a list of lists. All of the assocaited sets of sources

        """
        self.log.debug('starting the ``_extract_all_sets_from_list`` method')

        matchIndices1, matchIndices2, seps = self.mesh.match(
            ra1=self.ra,
            dec1=self.dec,
            ra2=self.ra,
            dec2=self.dec,
            radius=self.radius,
            maxmatch=0,  # 1 = match closest 1, 0 = match all,
            convertToArray=self.convertToArray
        )

        anchorIndicies = set()
        childIndicies = set()
        allMatches = []
        thisMatch = None
        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
            if m1 not in anchorIndicies and m1 not in childIndicies:
                if thisMatch:
                    allMatches.append(thisMatch)
                thisMatch = [self.sourceList[m1]]
                anchorIndicies.add(m1)
            if m2 not in anchorIndicies and m2 not in childIndicies:
                childIndicies.add(m2)
                thisMatch.append(self.sourceList[m2])
        if thisMatch:
            allMatches.append(thisMatch)

        self.log.debug('completed the ``_extract_all_sets_from_list`` method')
        return allMatches
