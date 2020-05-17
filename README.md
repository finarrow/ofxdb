# OFXDB

![Finarrow](https://github.com/finarrow/finarrow/blob/master/docs/media/finarrow_logo.png)

Database Generator for OFX Financial Statement Data, by [Finarrow].

## What is it?
`ofxdb` is a Python package providing ETL infrastructure needed 
to create a database of personal financial data. It uses 
[ofxtools] to connect to financial institutions and retrieve 
[ofx] files that are parsed into various csv files. The 
project's goal is to serve as the basis for making better personal 
finance decisions by providing a seamless and safe way to aggregate 
your account history across any financial institution and make the 
data available for you to analyze.

## Main features
These are few things that `ofxfdb` does in its current state:

 - Parse `ofxtools` account config file
 - Retrieve ofx files for all accounts in the `ofxtools` account config
 - Transform `ofxtools` account info and statement objects into csv files and save to disk

Current support:  
Account information  
Investment statements

To do:   
Bank statements  
Tax statements

Generates 5 csv files in your $HOME directory as follows:  

```sh
$HOME/ofxdb/account_info.csv  
$HOME/ofxdb/positions.csv  
$HOME/ofxdb/transactions.csv  
$HOME/ofxdb/balances.csv  
$HOME/ofxdb/securities.csv  
```

For more details, take a look at the [tables guide], [column definitions] and [table samples].

## Limitations
`ofxdb` is well-tested with TD Ameritrade accounts that hold only stocks and ETFs. 
By design `ofxdb` should work well for any broker that you can connect to with `ofxtools` and 
for any security types supported by the ofx protocol. 
If you encounter any issues, please [open an issue] against `ofxdb` on GitHub.

## Where to get it
The source code is currently hosted on GitHub at:
https://github.com/finarrow/ofxbd

Binary installer for the latest released version is available at the 
[Python package index].

```sh
pip install ofxdb
```

## Dependencies
- [ofxtools]
- [pandas]
- [keyring]

## Getting started

Set up your account credentials in your system keyring using the 
`ofxtools` command line tool `ofxget`. Do this for all accounts you would 
like to aggregate data for. You will be prompted in the command line to 
enter your password.

```sh
ofxget acctinfo <server_nickname> -u <your_username> --write --savepass
```

You can get a list of available server nicknames as follows:

```sh
ofxget list
```

Use the generate script to build the tables.

```sh
python ofxdb/data/generate.py
```

Check out the [ofxtools documentation] if you have any issues using `ofxget`.

## Getting involved

Discuss `ofxdb` on the [Finarrow community Slack]

We welcome your contributions. To file a bug, suggest an improvement, or 
request a new feature please [open an issue] against `ofxdb` on GitHub.

## License
[MIT](LICENSE)

<!-- Named links -->
[Finarrow]: https://github.com/finarrow
[open an issue]: https://github.com/finarrow/ofxdb/issues
[Finarrow community Slack]: https://join.slack.com/t/finarrow/shared_invite/zt-edx8c7hh-ALm_vWUpGpsAhwEjzKkWXg
[ofxtools]: https://github.com/csingley/ofxtools
[pandas]: https://pandas.pydata.org/
[keyring]: https://pypi.org/project/keyring/
[Python package index]: https://pypi.org/project/ofxdb
[tables guide]: https://github.com/finarrow/ofxdb/blob/master/doc/TABLES.md
[table samples]: https://github.com/finarrow/ofxdb/blob/master/doc/table_samples/
[ofx]: https://www.ofx.net/
[ofxtools]: https://github.com/csingley/ofxtools
[ofxtools documentation]: https://ofxtools.readthedocs.io/en/latest/
[column definitions]: https://github.com/finarrow/ofxdb/blob/master/doc/COLUMN_DEFINITIONS.md