#!python

import os
import datetime
import pandas as pd
from decimal import Decimal

from ofxtools.Parser import OFXTree
import ofxtools.models

from ofxdb.data import accounts
from ofxdb.utils import file_util
from ofxdb import cfg

# ToDo: imply xml.ETree attributes from the class
ETREE_ATTRS = [
    'elements',
    'listitems',
    'optionalMutexes',
    'requiredMutexes',
    'spec',
    'spec_no_listitems',
    'subaggregates',
    'unsupported'
]


# TODO: Document the need for this
def get_attr_mask(node, a):
    try:
        return getattr(node, a)
    except Exception as err:
        print(err)
        return None


def get_ofx_attrs(node):
    """
    Get object attributes excluding callable attributes, attributes that are inherited from the xml.ETree class, and
    hidden class attributes
    :param node: ofxtools model class
    :type node: ofxtools.models.base.Aggregate, ofxtools.models.base.SubAggregate
    :return: list of attribute strings
    :rtype: list
    """
    return [
        a for a in dir(node) if not callable(get_attr_mask(node, a)) and not a.startswith('_') and a not in ETREE_ATTRS
    ]


def is_ofx_obj(node):
    """
    Check if node is an ofxtools object
    :param node: ofxtools tree node
    :type node: object
    :return: is ofx object
    :rtype: bool
    """
    if isinstance(node, ofxtools.models.base.Aggregate):
        return True
    if isinstance(node, ofxtools.models.base.SubAggregate):
        return True
    return False


def append_attrs(node, record, label):
    """
    Append OFX object attributes to record dict
    :param node: ofxtools tree node
    :type node: object
    :param record: ofxtools model attribute object record dict
    :type record: dict
    :param label: record entry label for given node
    :type label: str
    :return: record with appended value(s) for node attributes
    :rtype: dict
    """
    if is_ofx_obj(node):
        for sub_node in get_ofx_attrs(node):
            new_node = get_attr_mask(node, sub_node)
            if new_node is not None:
                record = append_attrs(node=new_node, record=record, label=sub_node)
    else:
        if label in record:
            raise ValueError(
                'Label ({label}) for node ({node})already in record\n{record}'.format(
                    label=label, node=node, record=record
                )
            )
        if isinstance(node, Decimal):
            record[label] = float(node)
        elif isinstance(node, str):
            record[label] = str(node)
        elif isinstance(node, datetime.datetime):
            record[label] = node.replace(tzinfo=datetime.timezone.utc)
        elif node is None:
            return record
        else:
            raise ValueError('Unknown type ({cur_type}) encountered.'.format(cur_type=type(node)))

    return record


def get_obj_record(ofx_obj, acct_info):
    """
    Get record from OFX object attributes
    :param ofx_obj: ofxtools model class
    :type ofx_obj: ofxtools.models.base.Aggregate, ofxtools.models.base.SubAggregate
    :param acct_info: account information (date, datetime, server, user, acctid)
    :type acct_info: dict
    :return: record with appended attribute key->value pairs
    :rtype: dict
    """
    record = acct_info.copy()
    for obj_attr in get_ofx_attrs(ofx_obj):
        node = get_attr_mask(ofx_obj, obj_attr)
        if node is not None:
            record = append_attrs(node=node, record=record, label=obj_attr)
    return record


def get_list_records(ofx_objs, acct_info):
    """
    Get records from list of OFX objects
    :param ofx_objs: list of ofxtools model classes
    :type ofx_objs: list
    :param acct_info: account information (date, datetime, server, user, acctid)
    :type acct_info: dict
    :return: list of records with appended attribute key->value pairs
    :rtype: list
    """
    records = []
    for obj in ofx_objs:
        records.append(get_obj_record(obj, acct_info))
    return records


def get_records(ofx_obj, acct_info):
    """
    Get record from OFX object attributes
    :param ofx_obj: ofxtools model class or list of ofxtools model classes
    :type ofx_obj: list, ofxtools.models.base.Aggregate, ofxtools.models.base.SubAggregate
    :param acct_info: account information (date, datetime, server, user, acctid)
    :type acct_info: dict
    :return: list of records with appended attribute key->value pairs
    :rtype: list
    """
    if len(ofx_obj):
        return get_list_records(ofx_objs=ofx_obj, acct_info=acct_info)
    else:
        print('is not list')
        return [get_obj_record(ofx_obj=ofx_obj, acct_info=acct_info)]


def write_records(records, file_name):
    """
    Write records to disk (append to existing table)
    :param records: list of records
    :type records: list
    :param file_name: destination file name
    :type file_name: str
    :return: None
    """
    new_df = pd.DataFrame(records).set_index('date')
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, index_col='date')
        df = df.append(new_df)
    else:
        df = new_df
    print('Writing: {file_name}'.format(file_name=file_name))
    df.to_csv(file_name)
    return None


def process_ofx_obj(ofx_obj, acct_info, table, dbdir):
    """
    Process OFX object. 1) Get records from object. 2) Get destination file. 3) Write records to disk.
    :param ofx_obj: ofxtools model class or list of ofxtools model classes
    :type ofx_obj: list, ofxtools.models.base.Aggregate, ofxtools.models.base.SubAggregate
    :param acct_info: account information (date, datetime, server, user, acctid)
    :type acct_info: dict
    :param table: table name
    :type table: str
    :param dbdir: database directory
    :type dbdir: str
    :return: None
    """
    records = get_records(ofx_obj=ofx_obj, acct_info=acct_info)
    if records:
        file_name = file_util.get_table_file(table, dbdir=dbdir)
        write_records(records, file_name)

    return None


def agg(dbdir):
    parser = OFXTree()
    user_cfg = accounts.get_user_cfg()
    for server, server_config in user_cfg.items():
        if server != 'DEFAULT':
            user = server_config['user']
            file_name = '{dbdir}/stmt/current_{server}_{user}.ofx'.format(dbdir=dbdir, server=server, user=user)
            with open(file_name, 'rb') as f:
                parser.parse(f)
            ofx = parser.convert()
            statements = ofx.statements
            dt = datetime.datetime.today()
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            date = dt.date()
            acct_info = {'date': date, 'datetime': dt, 'server': server, 'user': user}
            for stmt in statements:
                # NOTE: acct_info yields only one record but get records returns list for ease handling downstream
                acct_info_records = get_records(ofx_obj=stmt.account, acct_info=acct_info)
                if len(acct_info_records) > 1:
                    raise Exception(
                        'Expected get_records to yield 1 record for acct_info, but got:\n{records}'.format(
                            records=acct_info_records
                        )
                    )
                cur_acct_info = acct_info_records[0]
                if 'acctid' not in cur_acct_info:
                    raise ValueError('Statement account info did not contain acctid.\n{stmt}'.format(stmt=stmt))
                acct_info_file = file_util.get_table_file('acct_info', dbdir=dbdir)
                write_records(acct_info_records, acct_info_file)

                procs = [
                    ('transactions', stmt.transactions),
                    ('positions', stmt.positions),
                    ('balances', stmt.balances.ballist)
                ]
                for table, ofx_obj in procs:
                    process_ofx_obj(ofx_obj=ofx_obj, acct_info=cur_acct_info, table=table, dbdir=dbdir)

            process_ofx_obj(ofx_obj=ofx.securities, acct_info=acct_info, table='securities', dbdir=dbdir)


if __name__ == '__main__':

    agg(cfg.DB_DIR)
