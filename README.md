title: Alfred-Convert Help

# Alfred-Convert #

Convert between different units in [Alfred 2](http://www.alfredapp.com/).

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot1.png "")

Alfred-Convert uses a [built-in library](http://pint.readthedocs.org/en/latest/index.html) to do the conversion offline.

**Note:** Currency conversions do require occasional Internet connectivity to update exchange rates. **Alfred-Convert** will otherwise work just fine without an Internet connection.

## Downloading ##

Download from [GitHub](https://github.com/deanishe/alfred-convert/blob/master/Convert.alfredworkflow?raw=true).

## Usage ##

The syntax is simple: the quantity, the unit you want to convert from then the unit you want to convert to. For example:

- `conv 128 mph km`
- `conv 72in cm`
- `conv 100psi bar`
- `conv 20.5 m/s mph`

It doesn't matter if there is a space between the quantity and the units or not. **Alfred-Convert** will tell you if it doesn't understand your query or know the units.

Actioning an item (selecting it and hitting `ENTER`) will copy it to the clipboard.

Use `convhelp` to view the built-in help file (this file) and `convcurrencies` to view and search the list of supported currencies.

## Screenshots ##

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot1.png "")

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot2.png "")

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot3.png "")

## Supported units ##

Currently, **Alfred-Convert** only supports [the units](https://raw.github.com/deanishe/alfred-convert/master/src/pint/default_en.txt) understood by the underlying [Pint](http://pint.readthedocs.org/en/latest/index.html) library (plus currencies).

If you'd like to see more units added, please create a corresponding [GitHub issue](https://github.com/deanishe/alfred-convert/issues).

### Supported currencies ###

To convert, use the appropriate **abbreviation** for the relevant currencies.

You can also view (and search) the list from within Alfred using the keyword `convcurrencies`.

|          Name         | Abbreviation |
|-----------------------|--------------|
| Australian dollar     | AUD          |
| Bulgarian lev         | BGN          |
| Brasilian real        | BRL          |
| Canadian dollar       | CAD          |
| Swiss franc           | CHF          |
| Chinese yuan renminbi | CNY          |
| Czech koruna          | CZK          |
| Danish krone          | DKK          |
| Euro                  | EUR          |
| Pound sterling        | GBP          |
| Hong Kong dollar      | HKD          |
| Croatian kuna         | HRK          |
| Hungarian forint      | HUF          |
| Indonesian rupiah     | IDR          |
| Israeli shekel        | ILS          |
| Indian rupee          | INR          |
| Japanese yen          | JPY          |
| South Korean won      | KRW          |
| Lithuanian litas      | LTL          |
| Mexican peso          | MXN          |
| Malaysian ringgit     | MYR          |
| Norwegian krone       | NOK          |
| New Zealand dollar    | NZD          |
| Philippine peso       | PHP          |
| Polish zloty          | PLN          |
| New Romanian leu      | RON          |
| Russian rouble        | RUB          |
| Swedish krona         | SEK          |
| Singapore dollar      | SGD          |
| Thai baht             | THB          |
| Turkish lira          | TRY          |
| US dollar             | USD          |
| South African rand    | ZAR          |

## Thanks, copyright, licensing ##

The Python [Pint](http://pint.readthedocs.org/en/latest/index.html) library does all the heavy lifting. See the [Pint GitHub repo](https://github.com/hgrecco/pint) for Pint licensing or `LICENSE.txt` and `AUTHORS.txt` in the `pint` subdirectory.

The money icon is from [Gettyicons.com](http://www.gettyicons.com/free-icon/105/money-icon-set/free-money-icon-png/) and was created by [DaPino](http://www.dapino-colada.nl/).

Exchange rates are downloaded from the [European Central Bank's website](http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html).

All other code/media are released under the [MIT Licence](http://opensource.org/licenses/MIT).
