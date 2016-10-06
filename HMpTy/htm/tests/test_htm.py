import os
import nose
import shutil
import yaml
from HMpTy import htm, cl_utils
from HMpTy.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="HMpTy",
    tunnel=False
)
arguments, settings, log, dbConn = su.setup()

# # load settings
# stream = file(
#     "/Users/Dave/.config/HMpTy/HMpTy.yaml", 'r')
# settings = yaml.load(stream)
# stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

# load settings
stream = file(
    pathToInputDir + "/example_settings.yaml", 'r')
settings = yaml.load(stream)
stream.close()

import shutil
try:
    shutil.rmtree(pathToOutputDir)
except:
    pass

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)

# xt-setup-unit-testing-files-and-folders


class test_htm():

    def test_htm_function(self):

        from HMpTy.htm import HTM
        mesh16 = HTM(
            depth=16,
            log=log
        )
        mesh20 = HTM(
            depth=20,
            log=log
        )
        print "DEPTH16:", mesh16.depth
        print "AREA16:", mesh16.area * 60 * 60 * 60 * 60, " arcsec^2"
        print "DEPTH20:", mesh20.depth
        print "AREA20:", mesh20.area * 60 * 60 * 60 * 60, " arcsec^2"

        overlappingTrixels = mesh16.intersect(
            ra="23:25:53.56",
            dec="+26:54:23.9",
            radius=1,
            inclusive=False
        )
        print overlappingTrixels

        overlappingTrixels = mesh16.intersect(
            ra="23:25:53.56",
            dec="+26:54:23.9",
            radius=10 / (60 * 60),
            inclusive=True
        )
        print overlappingTrixels

        twoArcsec = 2.0 / 3600.
        raList1 = [200.0, 200.0, 200.0, 175.23, 21.36]
        decList1 = [24.3,  24.3,  24.3,  -28.25, -15.32]
        raList2 = [200.0, 200.0, 200.0, 175.23, 55.25]
        decList2 = [24.3 + 0.75 * twoArcsec, 24.3 + 0.25 * twoArcsec,
                    24.3 - 0.33 * twoArcsec, -28.25 + 0.58 * twoArcsec, 75.22]
        matchIndices1, matchIndices2, seps = mesh16.match(
            ra1=raList1,
            dec1=decList1,
            ra2=raList2,
            dec2=decList2,
            radius=twoArcsec,
            maxmatch=0
        )

        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
            print raList1[m1], decList1[m1], " -> ", s * 3600., " arcsec -> ", raList2[m2], decList2[m2]

    def test_matcher_object(self):

        raList1 = ["13:20:00.00", 200.0, "13:20:00.00", 175.23, 21.36]
        decList1 = ["+24:18:00.00",  24.3,  "+24:18:00.00",  -28.25, -15.32]

        from HMpTy.htm import Matcher
        coordinateSet = Matcher(
            log=log,
            ra=raList1,
            dec=decList1,
            depth=16
        )

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

        print "NEARESRT MATCHES ONLY"
        matchIndices1, matchIndices2, seps = coordinateSet.match(
            ra=raList2,
            dec=decList2,
            radius=twoArcsec,
            maxmatch=1
        )
        for m1, m2, s in zip(matchIndices1, matchIndices2, seps):
            print raList1[m1], decList1[m1], " -> ", s * 3600., " arcsec -> ", raList2[m2], decList2[m2]

    def test_htm_function_exception(self):

        from HMpTy import htm
        try:
            this = htm(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
