#!/usr/local/bin/python
# encoding: utf-8
"""
*Given a list of coordinates and a crossmatch radius, split the list up into sets of associated locations*

:Author:
    David Young

:Date Created:
    October 12, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools


class sets():
    """
    *Given a list of coordinates and a crossmatch radius, split the list up into sets of associated locations*

    **Key Arguments:**
        - ``log`` -- logger
        - ``ra`` -- a list of the corrdinate right ascensions
        - ``dec`` -- a list of the corrdinate declinations (same length as ``ra``)
        - ``radius`` -- the radius to crossmatch the list of coordinates against itself (degrees)
        - ``sourceList`` -- the list of source imformation to be divided into associated sets (same length as ``ra`` and ``dec``)

    **Usage:**

        Given a list of transient metadata (any list, possibly a list of dictionaries) you can divide the list to assoicated sets of transients by running the following code:

        .. code-block:: python 

            from HMpTy.htm import sets
            xmatcher = sets(
                log=log,
                ra=raList,
                dec=decList,
                radius=10 / (60. * 60.),
                sourceList=transientList
            )
            allMatches = xmatcher.match 

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
    ):
        self.log = log
        log.debug("instansiating a new 'sets' object")
        self.ra = ra
        self.dec = dec
        self.radius = radius
        self.sourceList = sourceList
        # Initial Actions

        return None

    @property
    def match(
            self):
        """*all of the assocaited sets of sources*

        See the class for usage
        """

        return self._extract_all_sets_from_list()

    def _extract_one_set_from_list(
            self,
            ra,
            dec,
            radius,
            sourceList):
        """*Crossmatch the first row in the list against the remaining rows*

        **Key Arguments:**
            - ``ra`` -- a list of RAs
            - ``dec`` -- a list of DECs (same length as ``ra``)
            - ``radius`` -- the radius of the crossmatch
            - ``sourceList`` -- the list of source imformation to be divided into associated sets (same length as ``ra`` and ``dec``)

        **Return:**
            - ``matches`` -- the matches from the cross-match
            - ``ra`` -- the remaining RAs
            - ``dec`` -- the remaining DECs
        """
        self.log.info('starting the ``_extract_one_set_from_list`` method')

        matches = []

        from HMpTy import HTM
        mesh = HTM(
            depth=12,
            log=self.log
        )
        matchIndices1, matchIndices2, seps = mesh.match(
            ra1=ra[0],
            dec1=dec[0],
            ra2=ra[1:],
            dec2=dec[1:],
            radius=radius,
            maxmatch=0  # 1 = match closest 1, 0 = match all
        )

        matches = []
        matches.append(sourceList[0])

        indiciesToRemove = [0]

        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
            matches.append(sourceList[1:][m2])
            if (m2 + 1) not in indiciesToRemove:
                indiciesToRemove.append(m2 + 1)

        for index in sorted(indiciesToRemove, reverse=True):
            del ra[index]
            del dec[index]
            del sourceList[index]

        self.log.info('completed the ``_extract_one_set_from_list`` method')
        return matches, ra, dec, sourceList

    def _extract_all_sets_from_list(
            self):
        """*Extract all of the sets from the list of coordinates*

        **Return:**
            - ``allMatches`` -- a list of lists. All of the assocaited sets of sources
        """
        self.log.info('starting the ``_extract_all_sets_from_list`` method')

        allMatches = []

        matches, ra, dec, sourceList = self._extract_one_set_from_list(
            ra=self.ra[:],
            dec=self.dec[:],
            radius=self.radius,
            sourceList=self.sourceList[:]
        )
        allMatches.append(matches)

        while len(sourceList):
            matches, ra, dec, sourceList = self._extract_one_set_from_list(
                ra=ra,
                dec=dec,
                radius=self.radius,
                sourceList=sourceList
            )
            allMatches.append(matches)

        self.log.info('completed the ``_extract_all_sets_from_list`` method')
        return allMatches
