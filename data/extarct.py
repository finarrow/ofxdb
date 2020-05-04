#!python

import os
import datetime

from ofxdb.data import accounts
from ofxdb import cfg


def write_file(kind, server, user, db_dir=cfg.DB_DIR, verbose=False):
    kind = kind.lower()
    cmd = 'ofxget {kind} {server} -u {user}'.format(kind=kind, server=server, user=user)
    if kind in ['stmt']:
        cmd += ' --all'
    if verbose:
        print(cmd)
    stream = os.popen(cmd)
    output = stream.read()

    folder = '{db_dir}/{kind}/'.format(db_dir=db_dir, kind=kind)
    if not os.path.exists(folder):
        os.makedirs(folder)
    dt = datetime.datetime.today()
    dt = dt.replace(tzinfo=datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    file_name = '{folder}/{dt}_{server}_{user}.ofx'.format(folder=folder, dt=dt, server=server, user=user)
    current_name = '{folder}/current_{server}_{user}.ofx'.format(folder=folder, server=server, user=user)
    with open(file_name, 'w') as f:
        f.write(output)
    with open(current_name, 'w') as f:
        f.write(output)

    return None


def extract():
    user_cfg = accounts.get_user_cfg()
    for server, server_config in user_cfg.items():
        if server != 'DEFAULT':
            user = server_config['user']
            for kind in ['acctinfo', 'stmt']:
                write_file(kind=kind, server=server, user=user, verbose=True)


if __name__ == '__main__':

    extract()
