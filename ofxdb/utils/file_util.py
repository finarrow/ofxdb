#!python

import os
import pathlib

from ofxdb import cfg

"""
Constants
"""

TABLES = {
    'transactions': 'transactions.csv',
    'balances': 'balances.csv',
    'securities': 'securities.csv',
    'acct_info': 'account_info.csv',
    'positions': 'positions.csv',
}

"""
File location functions
"""


def get_table_file(table, dbdir=cfg.DB_DIR):
    base = '{dbdir}/tables'.format(dbdir=dbdir)
    if not os.path.exists(base):
        os.makedirs(base)
    table = table.lower()
    if table not in TABLES:
        raise ValueError(
            'Table ({table}) not supported. Try: {tables} or add support in {cur_file}.'.format(
                table=table, tables=list(TABLES.keys()), cur_file=pathlib.Path(__file__).absolute()
            )
        )
    table_file = '{base}/{table}'.format(base=base, table=TABLES.get(table))
    return table_file


if __name__ == '__main__':
    for t in list(TABLES.keys()) + ['break!']:
        print(get_table_file(table=t))
