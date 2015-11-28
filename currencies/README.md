
# Currencies #

`currencies_yahoo.py` throws a whole bunch of currencies at Yahoo! Finance, and saves a list of the ones it appears to know about.

|            File           |             Description             |
|---------------------------|-------------------------------------|
| `currencies_iso_4217.tsv` | All ISO 4217 currency codes         |
| `currencies_custom.tsv`   | Special currencies, e.g. Bitcoin    |
| `currencies_yahoo.tsv`    | Exchange rates offered by Yahoo!    |
| `currencies_yahoo.py`     | Script to generate above list       |
| `ISO 4217 List One.xlsx`  | Source list from the [ISO][iso4217] |

The first two TSV files are the input list of currencies. `currencies_yahoo.tsv` is the list of currencies that Yahoo! Finance has exchange rates for.

This file is the `currencies.tsv` file distributed with the workflow.

[iso4217]: http://www.iso.org/iso/home/standards/currency_codes.htm