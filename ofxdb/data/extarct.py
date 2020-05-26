#!python
"""OFX data extraction module.

Runs ofxget command line tool to retrieve OFX files from financial institutions. Saves files to
database directory defined in cfg.py.
"""
import os
import datetime

from ofxdb.data import accounts
from ofxdb import cfg

# -----------------------------------------------------------------------------
# -- File fetch method
# -----------------------------------------------------------------------------
_OFXGET_CMD = 'ofxget'
_OFXGET_USER_ARG = '-u'
_MULTI_OFX_TYPES = ['stmt']
_MULTI_OFX_ARGS = ' --all'


# TODO(ricrosales): Migrate to using ofxtools class to fetch instead of ofxget command line.
def fetch_file(ofx_type: str, server: str, user: str, verbose: bool = False) -> str:
    """Fetch OFX file from financial institutions server.

    Args:
        ofx_type: File type to fetch.
        server: ofxtools server nickname for financial institution.
        user: User name to fetch file for.
        verbose: Enable verbosity.

    Returns:
        A string containing ofx file contents. File has nested xml structure depending on file type.
    """
    ofx_type = ofx_type.lower()
    cmd = f'{_OFXGET_CMD} {ofx_type} {server} {_OFXGET_USER_ARG} {user}'
    if ofx_type in _MULTI_OFX_TYPES:
        cmd += _MULTI_OFX_ARGS
    if verbose:
        print(cmd)
    stream = os.popen(cmd)
    return stream.read()


# -----------------------------------------------------------------------------
# -- File write method
# -----------------------------------------------------------------------------
_FILE_DATETIME = '%Y%m%d-%H%M%S'


# TODO(ricrosales): Create symlink to current instead of copying file.
def write_file(
        ofx_file: str,
        ofx_type: str,
        server: str,
        user: str,
        db_dir: str = cfg.DB_DIR) -> None:
    """Write OFX file to disk.

    In addition to writing the file to the disk will write a copy with prefix "current" that is used
    downstream to identify the most recent file.

    Directory structure is enforced with full paths like:
    db_dir/ofx_type/YYYYMMDD-HHMMSS_server_user.ofx
    db_dir/ofx_type/current_server_user.ofx

    Args:
        ofx_file: OFX file as string.
        ofx_type: File type to fetch.
        server: ofxtools server nickname for financial institution.
        user: User name to fetch file for.
        db_dir: Database directory base path.

    Returns:
        None
    """
    folder = f'{db_dir}/{ofx_type}/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_date = datetime.datetime.today().replace(tzinfo=cfg.OFX_TIMEZONE).strftime(_FILE_DATETIME)
    file_name = f'{folder}/{file_date}_{server}_{user}.{cfg.OFX_EXTENSION}'
    current_name = f'{folder}/{cfg.CURRENT_PREFIX}_{server}_{user}.{cfg.OFX_EXTENSION}'
    with open(file_name, 'w') as file_buffer:
        file_buffer.write(ofx_file)
    with open(current_name, 'w') as file_buffer:
        file_buffer.write(ofx_file)


# -----------------------------------------------------------------------------
# -- File write method
# -----------------------------------------------------------------------------
_OFX_SUPPORTED_TYPES = ['acctinfo', 'stmt']


def extract(verbose: bool = False) -> None:
    """Extract all OFX data for all users and servers in the ofxtools user config.

    Args:
        verbose: Enable verbosity.

    Returns:
        None
    """
    user_cfg = accounts.get_user_cfg()
    for server, server_config in user_cfg.items():
        if server != cfg.OFXGET_DEFAULT_SERVER:
            user = server_config[cfg.OFXGET_CFG_USER_LABEL]
            for ofx_type in _OFX_SUPPORTED_TYPES:
                ofx_file = fetch_file(ofx_type=ofx_type, server=server, user=user, verbose=verbose)
                write_file(ofx_file=ofx_file, ofx_type=ofx_type, server=server, user=user)


if __name__ == '__main__':

    extract(verbose=True)
