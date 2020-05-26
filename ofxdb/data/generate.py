#!python
"""Script used to generate database."""
from ofxdb.data import extarct
from ofxdb.data import agg

if __name__ == '__main__':
    extarct.extract()
    agg.agg()
