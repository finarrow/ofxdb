"""Package-wide configuration file"""
import os
import pathlib
import datetime

from ofxtools import config as ofxtools_config

# -----------------------------------------------------------------------------
# -- Database definitions
# -----------------------------------------------------------------------------
DB_HOME = os.environ.get('HOME')
DB_DIR = f'{DB_HOME}/ofxdb'
CURRENT_PREFIX = 'current'
OFX_EXTENSION = 'ofx'

# -----------------------------------------------------------------------------
# -- ofxget definitions
# -----------------------------------------------------------------------------
OFXGET_CFG = ofxtools_config.USERCONFIGDIR / 'ofxget.cfg'
OFXGET_CFG_USER_LABEL = 'user'
OFXGET_DEFAULT_SERVER = 'DEFAULT'

# -----------------------------------------------------------------------------
# -- datetime definitions
# -----------------------------------------------------------------------------
OFX_TIMEZONE = datetime.timezone.utc

# -----------------------------------------------------------------------------
# -- System table definitions
# -----------------------------------------------------------------------------
AUX_TABLES_DIR = f'{os.path.dirname(pathlib.Path(__file__).absolute())}/aux_tables'
