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
    pathToScript=pathToInputDir + "/tcs_cat_ned_d_v13_1_0.sql",
    log=log,
    dbConn=dbConn
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
            primaryIdColumnName="primaryId",
            dbSettings=settings["database settings"]
        )
