from __future__ import division
from builtins import str
from past.utils import old_div
import os
import shutil
import yaml
import unittest
from HMpTy.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="hmpty"
)
arguments, settings, log, dbConn = su.setup()

# # load settings
# stream = open(
#     "/Users/Dave/.config/hmpty/hmpty.yaml", 'r')
# settings = yaml.load(stream)
# stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

# load settings
stream = open(
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

# THE DATA FOR THESE TESTES WAS GENERATED WITH THE FOLLOWING SQL QUERY:
"""select * from (select transientBucketId, raDeg, decDeg from transientBucket where transientBucketId > 1000 and raDEg is not null order by transientBucketId limit 3000) a order by rand();"""

import codecs
pathToReadFile = pathToInputDir + "test-data-for-sets.csv"
try:
    log.debug("attempting to open the file %s" % (pathToReadFile,))
    readFile = codecs.open(pathToReadFile, encoding='utf-8', mode='r')
    thisData = readFile.read().split("\n")
    readFile.close()
except IOError as e:
    message = 'could not open the file %s' % (pathToReadFile,)
    log.critical(message)
    raise IOError(message)


transientList = []
raList = []
decList = []
for l in thisData[1:]:
    l = l.split(",")
    if len(l) == 3:
        transientList.append(l)
        raList.append(l[1])
        decList.append(l[2])


class test_sets(unittest.TestCase):

    def test_sets_all_extract_function(self):

        from HMpTy.htm import sets
        xmatcher = sets(
            log=log,
            ra=raList,
            dec=decList,
            radius=old_div(10, (60. * 60.)),
            sourceList=transientList
        )
        allMatches = xmatcher._extract_all_sets_from_list()
        for i, m in enumerate(allMatches):
            pass
            #print(i, m)

    def test_sets_match_function(self):

        from HMpTy.htm import sets
        xmatcher = sets(
            log=log,
            ra=raList,
            dec=decList,
            radius=old_div(10, (60. * 60.)),
            sourceList=transientList
        )
        allMatches = xmatcher.match

    def test_sets_function_exception(self):

        from HMpTy.htm import sets
        try:
            this = sets(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception as e:
            assert True
            print(str(e))

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
