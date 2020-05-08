from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import yaml
from HMpTy.utKit import utKit
from fundamentals import tools
from os.path import expanduser
from past.utils import old_div
home = expanduser("~")

packageDirectory = utKit("").get_project_root()
settingsFile = packageDirectory + "/test_settings.yaml"

su = tools(
    arguments={"settingsFile": settingsFile},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName=None,
    defaultSettingsFile=False
)
arguments, settings, log, dbConn = su.setup()

# SETUP PATHS TO COMMON DIRECTORIES FOR TEST DATA
moduleDirectory = os.path.dirname(__file__)
pathToInputDir = moduleDirectory + "/input/"
pathToOutputDir = moduleDirectory + "/output/"

try:
    shutil.rmtree(pathToOutputDir)
except:
    pass
# COPY INPUT TO OUTPUT DIR
shutil.copytree(pathToInputDir, pathToOutputDir)

# Recursively create missing directories
if not os.path.exists(pathToOutputDir):
    os.makedirs(pathToOutputDir)

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
