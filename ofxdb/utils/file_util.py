#!python
"""Library of file utility methods."""
import os
import pathlib

import pandas as pd

from ofxdb import cfg

# -----------------------------------------------------------------------------
# -- Table file methods
# -----------------------------------------------------------------------------
# TODO (ricrosales): Remove the need for this by parsing the folder contents instead
TABLES = {
    'transactions': 'transactions.csv',
    'balances': 'balances.csv',
    'securities': 'securities.csv',
    'acct_info': 'account_info.csv',
    'account_info': 'account_info.csv',
    'positions': 'positions.csv',
}
AUX_TABLES = {
    'exposures': 'exposures.csv',
}


def table_file(table: str, db_dir: str = cfg.DB_DIR) -> str:
    """Retrieve full path for a given table.

    Args:
        table: Table name for file to retrieve.
        db_dir: Database base directory path.

    Returns:
        A string representing full path for location of table on the disk.

    Raises:
        ValueError: Encountered table that was not supported (in TABLES).
    """
    base_path = f'{db_dir}/tables'
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    table = table.lower()
    if table not in TABLES:
        raise ValueError(
            f'Table ({table}) not supported. Try: {list(TABLES.keys())} or add support in '
            f'{pathlib.Path(__file__).absolute()}.'
        )
    return f'{base_path}/{TABLES.get(table)}'


def aux_table_file(table: str, aux_dir: str = cfg.AUX_TABLES_DIR) -> str:
    """Retrieve full path for a given system table (part of the repo).

    Args:
        table: Table name for file to retrieve.
        aux_dir: Auxiliary table directory path.

    Returns:
        A string representing full path for location of table on the disk.

    Raises:
        FileNotFoundError: Unable to find the system aux_tables folder
        ValueError: Encountered table that was not supported (in TABLES).
    """
    if not os.path.exists(aux_dir):
        raise FileNotFoundError(f'Could not find the path for system aux_tables at: {aux_dir}')
    table = table.lower()
    if table not in AUX_TABLES:
        raise ValueError(
            f'Table ({table}) not supported. Try: {list(AUX_TABLES.keys())} or add support in '
            f'{pathlib.Path(__file__).absolute()}.'
        )
    return f'{aux_dir}/{AUX_TABLES.get(table)}'


# -----------------------------------------------------------------------------
# -- Table file read methods
# -----------------------------------------------------------------------------


def read_transactions(db_dir: str = cfg.DB_DIR) -> pd.DataFrame:
    """Read transactions to pandas DataFrame.

    Args:
        db_dir: Database base directory path.

    Returns:
        pandas DataFrame containing transactions data
    """
    file_name = table_file('transactions', db_dir=db_dir)
    return pd.read_csv(file_name, index_col=0)


def read_balances(db_dir: str = cfg.DB_DIR) -> pd.DataFrame:
    """Read balances to pandas DataFrame.

    Args:
        db_dir: Database base directory path.

    Returns:
        pandas DataFrame containing balance data
    """
    file_name = table_file('balances', db_dir=db_dir)
    return pd.read_csv(file_name, index_col=0)


def read_securities(db_dir: str = cfg.DB_DIR) -> pd.DataFrame:
    """Read securities to pandas DataFrame.

    Args:
        db_dir: Database base directory path.

    Returns:
        pandas DataFrame containing securities data
    """
    file_name = table_file('securities', db_dir=db_dir)
    return pd.read_csv(file_name, index_col=0)


def read_acct_info(db_dir: str = cfg.DB_DIR) -> pd.DataFrame:
    """Read account info to pandas DataFrame.

    Args:
        db_dir: Database base directory path.

    Returns:
        pandas DataFrame containing account info data
    """
    file_name = table_file('acct_info', db_dir=db_dir)
    return pd.read_csv(file_name, index_col=0)


def read_positions(db_dir: str = cfg.DB_DIR) -> pd.DataFrame:
    """Read positions to pandas DataFrame.

    Args:
        db_dir: Database base directory path.

    Returns:
        pandas DataFrame containing positions data
    """
    file_name = table_file('positions', db_dir=db_dir)
    return pd.read_csv(file_name, index_col=0)


def read_exposures() -> pd.DataFrame:
    """Read exposures to pandas DataFrame.

    Returns:
        pandas DataFrame containing exposure data
    """
    file_name = aux_table_file('exposures')
    return pd.read_csv(file_name, index_col=0)


if __name__ == '__main__':
    for t in list(TABLES.keys()):
        print(table_file(table=t))

    for t in list(AUX_TABLES.keys()):
        print(aux_table_file(table=t))

    READERS = [
        read_acct_info,
        read_balances,
        read_exposures,
        read_positions,
        read_securities,
        read_transactions,
    ]

    for read_func in READERS:
        print(read_func().head())
