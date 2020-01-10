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
    projectName="HMpTy"
)
arguments, settings, log, dbConn = su.setup()


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


from fundamentals.mysql import directory_script_runner
directory_script_runner(
    log=log,
    pathToScriptDirectory=pathToInputDir,
    databaseName=settings["database settings"]["db"],
    force=True,
    loginPath=settings["database settings"]["loginPath"],
    waitForResult=True
)

from fundamentals.mysql import writequery
sqlQuery = """ALTER TABLE tcs_cat_ned_d_v13_1_0 DROP COLUMN htm16ID, DROP COLUMN htm10ID, DROP COLUMN htm13ID"""
try:
    writequery(
        log=log,
        sqlQuery=sqlQuery,
        dbConn=dbConn
    )
except:
    pass


class test_add_htm_ids_to_mysql_database_table(unittest.TestCase):

    def test_add_htm_ids_to_mysql_database_table_function(self):

        from HMpTy.mysql import add_htm_ids_to_mysql_database_table
        add_htm_ids_to_mysql_database_table(
            raColName="raDeg",
            declColName="decDeg",
            tableName="tcs_cat_ned_d_v13_1_0",
            dbConn=dbConn,
            log=log,
            primaryIdColumnName="primaryId"
        )
