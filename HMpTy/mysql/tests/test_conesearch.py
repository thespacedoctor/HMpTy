from __future__ import print_function
from builtins import str
import os
import unittest
import shutil
import yaml
from HMpTy.utKit import utKit
from fundamentals import tools
from os.path import expanduser
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

# RELOAD TEST DATA
from fundamentals.mysql import execute_mysql_script
exception = execute_mysql_script(
    pathToScript=pathToInputDir + "/transientBucket.sql",
    log=log,
    dbConn=dbConn
)


class test_conesearch(unittest.TestCase):

    def test_get_trixel_ids_that_overlap_conesearch_circles(self):

        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra="23:25:53.56",
            dec="+26:54:23.9",
            radiusArcsec=5
        )
        print("SINGLE COORDINATE CONESEARCH TRIXEL IDs")
        print(cs._get_trixel_ids_that_overlap_conesearch_circles())

        raList1 = ["13:20:00.00", 200.0, "13:20:00.00", 175.23, 21.36]
        decList1 = ["+24:18:00.00",  24.3,  "+24:18:00.00",  -28.25, -15.32]

        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra=raList1,
            dec=decList1,
            radiusArcsec=5
        )
        print("COORDINATE LIST CONESEARCH TRIXEL IDs")
        print(cs._get_trixel_ids_that_overlap_conesearch_circles())

    def test_conesearch_function(self):

        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra="23:25:53.56",
            dec="+26:54:23.9",
            radiusArcsec=5
        )
        print(cs.query)

    def test_conesearch_function2(self):

        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra=351.47321,
            dec=26.90664,
            radiusArcsec=5
        )
        print(cs.query)

    def test_conesearch_function3(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra=raList1,
            dec=decList1,
            radiusArcsec=10,
            separations=True
        )
        matchIndies, matches = cs.search()
        for row in matches.list:
            print(row)

    def test_conesearch_function4(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra=raList1,
            dec=decList1,
            radiusArcsec=7200
        )
        matchIndies, matches = cs.search()

    def test_conesearch_distinct_function(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

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
            distinct=True
        )
        matchIndies, matches = cs.search()
        for row in matches.list:
            print(row)

    def test_conesearch_sql_where_function(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        print("WHERE CLAUSE ADDED")
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
            distinct=False,
            sqlWhere="spectralType is not null"
        )
        matchIndies, matches = cs.search()
        for row in matches.list:
            pass
            print(row)

    def test_conesearch_sql_where_function2(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        print("WHERE CLAUSE ADDED & DISTINCT")
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
            pass
            print(row)

    def test_documentaion_function(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        print("TUTORIAL")
        from HMpTy.mysql import conesearch
        cs = conesearch(
            log=log,
            dbConn=dbConn,
            tableName="transientBucket",
            columns="transientBucketId, spectralType",
            ra=raList1,
            dec=decList1,
            radiusArcsec=10,
            separations=False,
            distinct=False,
            sqlWhere=False
        )
        print(cs.query)
        matchIndies, matches = cs.search()
        for row in matches.list:
            pass
            print(row)

    def test_documentaion_functio2(self):

        raList1 = ["23:25:53.56",  "02:10:08.16",
                   "13:20:00.00", 1.47329, 35.34279]
        decList1 = ["+26:54:23.9",  "-48:38:24.3",
                    "+24:18:00.00",  8.43016, -42.34428]

        print("TUTORIAL")
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
        print(cs.query)
        matchIndies, matches = cs.search()
        for row in matches.list:
            pass
            print(row)

        print(matches.table())
        matches.table(filepath=pathToOutputDir + "results.dat")

        print(matches.mysql(tableName="mysql_table", filepath=None))

    def test_conesearch_function_exception(self):

        from HMpTy.mysql import conesearch
        try:
            this = conesearch(
                log=log,

                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception as e:
            assert True
            print(str(e))

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
