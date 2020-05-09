#!python

from ofxdb.data import extarct
from ofxdb.data import agg
from ofxdb import cfg

if __name__ == '__main__':
    extarct.extract()
    agg.agg(cfg.DB_DIR)
