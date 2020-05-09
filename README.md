# ofxdb

DB Generator for OFX Financial Statement Data

Current support:
-----------
Investment statements

ToDo:
-----------
Bank statements  
Tax statements

Generates data for 5 tables
-----------
TRANSACTIONS  
POSITIONS  
ACCOUNT_INFO  
BALANCES  
SECURITIES  

TRANSACTIONS:  
-----------
* statement (list) -> transactions  
  * transactions[n] (obj) -> (getattr) -> transaction_obj (e.g. INVBUY, INVTRAN, INVSELL, etc.)  
    * transaction_obj (obj) -> (getattr) -> transaction_attr (e.g. SECID, units, etc.)  
      * tranaction_attr (obj) -> (getattr) -> obj_attr (e.g. SECID.uniqueid. SECID.uniqueidtype, etc.)  
        * obj_attr (str) -> obj.value  
      * transaction_attr (float) -> value  
      * transaction_attr (str) -> value  
  * transactions[n] (obj) -> (getattr) -> transaction_attr (e.g. buytype, selltype, etc.)  
    * transaction_attr (str) -> value  

e.g.  
 datetime | username | brokerid | acctid | trans | buytype | selltype | ... | secid.uniqueid | ...  

POSITIONS:  
-----------
* statement (list) -> positions  
  * positions[n] (obj) -> (getattr) -> position_obj (e.g. POSSTOCK)  
    * position_obj (obj) -> (getattr) -> position_attr (e.g. SECID, units, etc.)  
      * position_attr (obj) -> (getattr) -> obj_attr (e.g. SECID.uniqueid or SECID.uniqueidtype)  
        * obj_attr (str) -> value  
      * position_attr (float) -> value (for any other position_attr that is Decimal)  

e.g.  
datetime | username | brokerid | acctid | type | ... | postype | secid.uniqueid | ... | units  

ACCOUNT INFO:  
-----------
* statement (obj) -> acct_obj  
  * acct_obj (obj) -> (getattr) -> acct_attr (e.g. acctid, brokerid, etc.)  
    * acct_attr (str) -> value (for any other acct_attr that is str)  
    * acct_attr (float) -> value (for any other transaction_attr that is Decimal)  

e.g.  
username | brokerid | acctid  

BALANCES:  
-----------
* statement (obj) -> balances_obj  
  * balances_obj (list) -> (getattr) -> ballist  
    * ballist[n] (obj) -> (getattr) -> bal_obj (e.g. BAL)  
      * bal_obj -> (getattr) -> bal_attr (e.g. baltype, value, etc.)  
        * bal_attr -> (str) -> value (for ant other bal_attr that is str)  
        * bal_attr -> (float) -> value (for any other bal_attr that is Decimal)  
  * balances_obj (obj) -> (getattr) -> balances_attr (e.g. availcash, buypower)  
    * balances_attr (float) -> value  

e.g.  
username | brokerid | acctid | baltype | value  

SECURITIES:  
-----------
* ofx_file (list) -> securities  
  * securities[n] (obj) -> (getattr) -> securities_obj (e.g. STOCKINFO)  
    * securities_obj (obj) -> (getattr) -> securities_attr (e.g. assetclass, SECINFO, etc.)  
      * securities_attr (obj) -> (getattr) -> obj2_attr (e.g. SECID, secname, ticker, etc.)  
        * obj2_attr (obj) -> (getattr) -> obj2_attr (e.g. uniqueid, uniqueidtype, etc.)  
          * obj2_attr (str) -> obj2.value  
        * obj_attr (str) -> value  
      * securities_attr (str) -> value (for any other securities_attr that is str)  

e.g.  
username | brokerid | acctid | ... | secid.uniqueid | secid.uniqueidtype | ...  
