#!python
"""Library of file utility methods."""
import os
import pathlib

from ofxdb import cfg

# -----------------------------------------------------------------------------
# -- Table file methods
# -----------------------------------------------------------------------------
TABLES = {
    'transactions': 'transactions.csv',
    'balances': 'balances.csv',
    'securities': 'securities.csv',
    'acct_info': 'account_info.csv',
    'positions': 'positions.csv',
}


def get_table_file(table: str, db_dir: str = cfg.DB_DIR) -> str:
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
    table_file = f'{base_path}/{TABLES.get(table)}'
    return table_file


if __name__ == '__main__':
    for t in list(TABLES.keys()) + ['break!']:
        print(get_table_file(table=t))
