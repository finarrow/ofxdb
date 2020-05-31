#!python
import argparse
from typing import Union

import numpy as np
import pandas as pd

from ofxdb.utils import file_util
from ofxdb.data import extarct, agg


def risk(acctid: Union[list, None] = None) -> pd.DataFrame:
    """Compute risk of aggregate portfolio.

    Args:
        acctid: Account IDs

    Returns:
        pandas DataFrame with portfolio risk statistics.
    """
    exposures = file_util.read_exposures()
    positions = file_util.read_positions()
    securities = file_util.read_securities()

    securities = securities.drop_duplicates(['ticker', 'date'], keep='last')
    securities = securities[['date', 'uniqueid', 'uniqueidtype', 'ticker']]

    if acctid is not None:
        positions = positions[positions['acctid'].isin(acctid)]
    positions = positions.drop_duplicates(
        subset=['date', 'acctid', 'uniqueid', 'uniqueidtype'], keep='last')
    portfolio = positions[positions['date'] == positions['date'].max()]
    portfolio = portfolio.groupby(['date', 'uniqueidtype', 'uniqueid']).sum()[['mktval', 'units']]
    portfolio = portfolio.reset_index()
    portfolio = portfolio.merge(securities, on=['date', 'uniqueid', 'uniqueidtype'], how='left')
    portfolio = portfolio.merge(exposures, on='ticker', how='left')

    portfolio['MV($)'] = portfolio['mktval']
    portfolio['NetMV($)'] = portfolio['MV($)'] * np.sign(portfolio['leverage'])
    portfolio['GrossMV($)'] = portfolio['MV($)'] * np.abs(portfolio['leverage'])
    portfolio['BAGMV($)'] = portfolio['MV($)'] * portfolio['beta']
    portfolio['NetGrossMV($)'] = portfolio['MV($)'] * portfolio['leverage']

    portfolio = portfolio.rename(columns={'date': 'Date'})
    portfolio_summary = portfolio.groupby('Date').sum()
    portfolio_summary = portfolio_summary[
        ['MV($)', 'GrossMV($)', 'BAGMV($)', 'NetMV($)', 'NetGrossMV($)']]
    portfolio_summary['Gross(%)'] = 100 * (
            portfolio_summary['GrossMV($)'] / portfolio_summary['MV($)'])
    portfolio_summary['BAG(%)'] = 100 * (
            portfolio_summary['BAGMV($)'] / portfolio_summary['MV($)'])
    portfolio_summary['NetMV(%)'] = 100 * (
            portfolio_summary['NetMV($)'] / portfolio_summary['MV($)'])
    portfolio_summary['NetGrossMV(%)'] = 100 * (
            portfolio_summary['NetGrossMV($)'] / portfolio_summary['MV($)'])

    for col in portfolio_summary.columns:
        portfolio_summary[col] = portfolio_summary[col].round(2)

    headers = ['Date', portfolio_summary.index[0]]
    return portfolio_summary.T.to_markdown(
        headers=headers, tablefmt='fancy_grid', numalign='right', floatfmt=',.2f')


if __name__ == '__main__':
    VIEWS = {
        'risk': risk
    }
    description = 'View aggregated account data.'
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument(
        '-view', type=str, default=VIEWS.keys(), nargs='+', help='View(s) to show.')
    arg_parser.add_argument(
        '-acctid', type=str, default=None, nargs='+', help='Account ID(s) to show.')
    arg_parser.add_argument(
        '--refresh',
        dest='refresh',
        action='store_const',
        const=True,
        default=False,
        help='Refresh data.')
    args = arg_parser.parse_args()

    if args.refresh:
        extarct.extract()
        agg.agg()

    for view in args.view:
        print(VIEWS[view](args.acctid))
