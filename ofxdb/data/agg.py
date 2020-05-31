#!python
"""OFX file aggregation module.

Retrieves the latest OFX files for all institutions and appends them to the corresponding table.

Loads data into 5 aux_tables (see docs for descriptions):
account_info.csv
balances.csv
positions.csv
securities.csv
transactions.csv
"""
import os
import datetime
from decimal import Decimal
from typing import Union, List

import pandas as pd
from ofxtools.Parser import OFXTree
from ofxtools.models import Aggregate, SubAggregate

from ofxdb.data import accounts
from ofxdb.utils import file_util
from ofxdb import cfg

# -----------------------------------------------------------------------------
# -- Module-wide object definitions
# -----------------------------------------------------------------------------
_OFXToolsBaseModel = Union[Aggregate, SubAggregate]
_OFXToolsElement = Union[_OFXToolsBaseModel, str, Decimal, datetime.datetime, None]

# -----------------------------------------------------------------------------
# -- ofxtools model parsing helper methods
# -----------------------------------------------------------------------------


def getattr_mask(element: _OFXToolsBaseModel, attribute: str) -> Union[_OFXToolsElement, None]:
    """Mask for getattr method.

    Used to handle errors that are thrown when getattr fails due to encountering an ofxtools model
    that has no length. This can happen for example when there exists an account that was opened but
    never had transactions.

    For example, a KeyError thrown for the following elements:
    <INVTRANLIST dtstart='2018-05-25 18:01:21+00:00' dtend='2020-05-22 00:00:00+00:00' len=0>
    <INVPOSLIST()>

    Args:
        element: ofxtools model
        attribute: ofxtools model class attribute string

    Returns:
        An ofxtools element. Can be a new element or a leaf of the xml structure.
    """
    try:
        return getattr(element, attribute)
    except KeyError as _:
        return None


def get_ofx_attrs(element: _OFXToolsBaseModel) -> List[str]:
    """Get ofxtools object attributes.

    Excludes callable attributes, attributes that are inherited from the Aggregate class, and
    any private class attributes.

    Args:
        element: ofxtools model

    Returns:
        List of attribute strings
    """
    return [
        attribute for attribute in dir(element)
        if not callable(getattr_mask(element, attribute)) and
        not attribute.startswith('_') and
        attribute not in dir(Aggregate)
    ]


def is_ofx_model(element: _OFXToolsElement) -> bool:
    """Check if element is an ofxtools model.

    This is a wrapper for isinstance that accounts for _OFXToolsBaseModel being a Union generic
    type.

    Args:
        element: ofxtools element tree element.

    Returns:
        True or False
    """
    if isinstance(element, _OFXToolsBaseModel.__args__):
        return True
    return False


# -----------------------------------------------------------------------------
# -- ofxtools model record generation helper methods
# -----------------------------------------------------------------------------


def append_model_records(element: _OFXToolsElement, record: dict, key: str) -> dict:
    """Recursively append OFX model attributes -> value pair to record dictionary.

    Args:
        element: ofxtools element tree element.
        record: ofxtools model attribute -> value dictionary.
        key: Record key for element.

    Returns:
        Appended record dictionary.

    Raises:
        KeyError: Encountered duplicate key (should not occur by OFX spec)
        ValueError: Encountered unrecognized type for leaf
    """
    if is_ofx_model(element):
        for sub_element in get_ofx_attrs(element):
            new_element = getattr_mask(element, sub_element)
            if new_element is not None:
                record = append_model_records(element=new_element, record=record, key=sub_element)
    else:
        if key in record:
            raise KeyError(f'Key ({key}) for element ({element}) already in record\n{record}')
        if isinstance(element, Decimal):
            record[key] = float(element)
        elif isinstance(element, str):
            record[key] = str(element)
        elif isinstance(element, datetime.datetime):
            record[key] = element.replace(tzinfo=cfg.OFX_TIMEZONE)
        elif element is None:
            return record
        else:
            raise ValueError(f'Unknown type ({type(element)}) encountered.')

    return record


def get_model_record(ofx_model: _OFXToolsBaseModel, acct_info: dict) -> dict:
    """Get record from OFX model attributes.

    Args:
        ofx_model: ofxtools model.
        acct_info: Account information dict (date, datetime, server, user, acctid).

    Returns:
        Model record with attribute key -> value pairs. All records seeded with account information.
    """
    record = acct_info.copy()
    for ofx_attr in get_ofx_attrs(ofx_model):
        element = getattr_mask(ofx_model, ofx_attr)
        if element is not None:
            record = append_model_records(element=element, record=record, key=ofx_attr)
    return record


def get_list_records(ofx_models: List[_OFXToolsBaseModel], acct_info: dict) -> List[dict]:
    """Get records from list of OFX models.

    Args:
        ofx_models: List of ofxtools models.
        acct_info: Account information dict (date, datetime, server, user, acctid).

    Returns:
        List of model records with attribute key -> value pairs.
    """
    return [get_model_record(model, acct_info) for model in ofx_models]


# -----------------------------------------------------------------------------
# -- Model processing helper methods
# -----------------------------------------------------------------------------
_INDEX_COL = 'datetime'
_OFX_ACCTID = 'acctid'


def generate_records(
        ofx_model: Union[_OFXToolsBaseModel, List[_OFXToolsBaseModel]],
        acct_info: dict) -> List[dict]:
    """Get records from OFX object attributes.

    This is a wrapper for get_list_records to handle generating one or multiple records.

    Args:
        ofx_model: ofxtools model or list of ofxtools models.
        acct_info: Account information dict (date, datetime, server, user, acctid).

    Returns:
        A list of records with model attribute key -> value pairs.
    """
    if len(ofx_model) > 0:
        # We check for len > 0 here to cover the case where ofx_model is a list of models and the
        # case where ofx_model is a generator of models (e.g. transactions, positions, etc.).
        return get_list_records(ofx_models=ofx_model, acct_info=acct_info)
    return [get_model_record(ofx_model=ofx_model, acct_info=acct_info)]


def write_records(records: List[dict], file_name: str) -> None:
    """Write records to disk, appending to existing table.

    Args:
        records: List of record dicts.
        file_name: Destination file name.

    Returns:
        None
    """
    # TODO (ricrosales): This should replace data for given account instead of just appending
    new_df = pd.DataFrame(records).set_index(_INDEX_COL)
    if os.path.exists(file_name):
        file_df = pd.read_csv(file_name, index_col=_INDEX_COL)
        file_df = file_df.append(new_df)
    else:
        file_df = new_df
    file_df.to_csv(file_name)


def process_ofx_model(
        ofx_model: Union[_OFXToolsBaseModel, List[_OFXToolsBaseModel]],
        acct_info: dict,
        table: str,
        db_dir: str) -> None:
    """Process OFX model.

    1) Generate records from ofxtools model.
    2) Get destination file.
    3) Write records to disk.

    Args:
        ofx_model: ofxtools model or list of ofxtools models.
        acct_info: Account information dict (date, datetime, server, user, acctid).
        table: Destination table name for given model.
        db_dir: Database base directory path.

    Returns:
        None
    """
    records = generate_records(ofx_model=ofx_model, acct_info=acct_info)
    if records:
        file_name = file_util.table_file(table, db_dir=db_dir)
        write_records(records, file_name)


def process_statement_model(stmt: _OFXToolsBaseModel, acct_info: dict, db_dir: str) -> None:
    """Process ofxtools statement model.

    1) Generate records from ofxtools model.
    2) Get destination file.
    3) Write records to disk.
    4) Process associated transactions, positions, and balances

    Args:
        stmt:
        acct_info:
        db_dir:

    Returns:
        None

    Raises:
        Exception: Encountered account_info record with multiple entries. This is not supposed to
                   occur based on OFX spec. Multiple accounts being supported would break assumption
                   made on seeding all model records with account info.
    """
    # acct_info should yield only one record but get records returns list for ease downstream
    acct_info_records = generate_records(ofx_model=stmt.account, acct_info=acct_info)
    if len(acct_info_records) > 1:
        raise Exception(
            f'Expected generate_records to yield 1 record for acct_info, '
            f'but got:\n{acct_info_records}'
        )
    cur_acct_info = acct_info_records[0]

    if _OFX_ACCTID not in cur_acct_info:
        raise ValueError(f'Statement account info did not contain acctid.\n{stmt}')
    acct_info_file = file_util.table_file('acct_info', db_dir=db_dir)
    write_records(acct_info_records, acct_info_file)

    statement_table_map = [
        (stmt.transactions, 'transactions'),
        (stmt.positions, 'positions'),
        (stmt.balances.ballist, 'balances')
    ]
    for ofx_model, table in statement_table_map:
        process_ofx_model(ofx_model=ofx_model, acct_info=cur_acct_info, table=table, db_dir=db_dir)


# -----------------------------------------------------------------------------
# -- OFX data aggregation method
# -----------------------------------------------------------------------------
_STMT_FOLDER = 'stmt'


def agg(db_dir: str = cfg.DB_DIR) -> None:
    """Aggregate current ofx files to the database.

    Args:
        db_dir:  Database base directory path.

    Returns:
        None
    """
    parser = OFXTree()
    user_cfg = accounts.get_user_cfg()
    for server, server_config in user_cfg.items():
        if server != cfg.OFXGET_DEFAULT_SERVER:
            user = server_config[cfg.OFXGET_CFG_USER_LABEL]
            file_name = f'{db_dir}/{_STMT_FOLDER}/' \
                        f'{cfg.CURRENT_PREFIX}_{server}_{user}.{cfg.OFX_EXTENSION}'
            with open(file_name, 'rb') as ofx_file:
                parser.parse(ofx_file)
            ofx = parser.convert()
            agg_datetime = datetime.datetime.today().replace(tzinfo=cfg.OFX_TIMEZONE)
            agg_date = agg_datetime.date()
            acct_info = {'datetime': agg_datetime, 'date': agg_date, 'server': server, 'user': user}
            for stmt in ofx.statements:
                process_statement_model(stmt=stmt, acct_info=acct_info, db_dir=db_dir)
            process_ofx_model(
                ofx_model=ofx.securities, acct_info=acct_info, table='securities', db_dir=db_dir
            )


if __name__ == '__main__':

    agg()
