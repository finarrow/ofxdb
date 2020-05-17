## Dataset Column Definitions

Check the [ofx downloads] for the most up to date spec. 
[OFX 2.2 spec] is the latest as of writing. 
We provide some guidance on interpretation below to help get you started.

# Account Info (shared)
 - `date` - data load date
 - `datetime` - timestamp for data load
 - `server` - server nickname (defined by `ofxtools`)
 - `user` - account username
 - `acctid` - account number
 - `brokerid` - ofx broker identification (e.g. ameritrade.com)

# Balances
 - `baltype` - units for balance, used to interpret `value` (e.g. DOLLAR)
 - `desc` - description of balance type (e.g. LongStock or MoneyMarket)
 - `dtasof` - effective date of the balance
 - `name` - balance name (same as `desc` in some cases)
 - `value` - balance value (units depend on `baltype`)

# Positions
 - `dtpriceasof` - effective date of `mktval` and `unitprice`
 - `heldinacct` - sub-account type (e.g. CASH, MARGIN, SHORT, OTHER)
 - `mktval` - market value of the position
 - `postype` - direction of position held
   - SHORT = Writer for options, Short for all others.
   - LONG = Holder for options, Long for all others.
 - `uniqueid` - unique security identifier value
 - `uniqueidtype` - security identifier type (e.g. CUSIP)
 - `unitprice` - security price
   - for stocks, MFs, other, price per share
   - bonds = percentage of par
   - option = premium per share of underlying security
 - `units` - quantity of security held in account
   - for stocks, MFs, other, number of shares held
   - bonds = face value
   - options = number of contracts

# Securities
 - `uniqueid` - unique security identifier value
 - `uniqueidtype` - security identifier type (e.g. CUSIP)
 - `secname` - full name of security
 - `ticker` - ticker symbol of security

# Transactions
 - `dtend` - account closure date
 - `dtstart` - account start date
 - `incometype` type of investment income
   - CGLONG (capital gains-long term)
   - CGSHORT (capital gains-short term)
   - DIV (dividend)
   - INTEREST
   - MISC
 - `dttrade` - trade date or for stock splits, the day of record
 - `fitid` - unique transaction id, assigned by financial institution
 - `memo` - other information about transaction
 - `uniqueid` - unique security identifier value
 - `uniqueidtype` - security identifier type (e.g. CUSIP)
 - `subacctfund` - type of account where the money for the transaction came from/went to 
 (e.g. CASH, MARGIN, SHORT, OTHER)
 - `subacctsec` - sub-account type for the security (e.g. CASH, MARGIN, SHORT, OTHER)
 - `total` - transaction total.
   - buys, sells, etc. = ((quan. * (price +/- markup/markdown)) +/- 
   (commission + fees + load + taxes + penalty + withholding + statewithholding))
   - distributions, interest, margin interest, misc. expense, etc. = amount
   - return of cap = cost basis
 - `buytype` - type of purchase (e.g. BUY, BUYTOCOVER)
 - `unitprice` - price per commonly-quoted unit. Does not include markup/markdown
 - `units` - quantity of security transacted
   - quantity for security-based actions other than stock splits
   - shares for stocks, mutual funds, and others
   - face value for bonds
   - contracts for options
 - `fees` - fees applied to trade
 - `selltype` - type of sell (e.g. SELL, SELLSHORT)
 - `dtposted` - date transaction was posted to account
 - `trnamt` - amount of transaction
 - `trntype` - transaction type, effect on account (e.g. CREDIT, DEBIT)
 - `postype` - direction of position held
   - SHORT = Writer for options, Short for all others
   - LONG = Holder for options, Long for all others
 - `tferaction` - Action for transfers (e.g. IN, OUT)

<!-- Named links -->
[ofx downloads]: https://www.ofx.net/downloads.html
[OFX 2.2 spec]: https://www.ofx.net/downloads/OFX%202.2.pdf