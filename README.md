
# Alfred-Convert #

Convert between different units in [Alfred 2][alfred].

![][demo]

Alfred-Convert uses a [built-in library](http://pint.readthedocs.org/en/latest/index.html) to do the conversion offline.

**Note:** Currency conversions do require occasional Internet connectivity to update exchange rates. Alfred-Convert will otherwise work just fine without an Internet connection.

- [Downloading](#downloading)
- [Usage](#usage)
- [Supported units](#supported-units)
    - [Supported currencies](#supported-currencies)
    - [Adding custom units](#adding-custom-units)
- [Thanks, copyright, licensing](#thanks-copyright-licensing)


## Downloading ##

Download from [GitHub][ghreleases] or [Packal.org][packal].

## Usage ##

The syntax is simple: the quantity, the unit you want to convert from then the unit you want to convert to. For example:

- `conv 128 mph km`
- `conv 72in cm`
- `conv 100psi bar`
- `conv 20.5 m/s mph`

It doesn't matter if there is a space between the quantity and the units or not. Alfred-Convert will tell you if it doesn't understand your query or know the units.

Actioning an item (selecting it and hitting `↩`) will copy it to the clipboard.
Using `⌘+L` will display the result in Alfred's large text window, `⌘+C` will
copy the selected result to the clipboard.

Use `convinfo` to view the built-in help file, view/search the list of
supported currencies, change the number of decimal places shown in conversions,
or edit your custom units.


## Supported units ##

Currently, Alfred-Convert only supports [the units][pintunits] understood
by the underlying [Pint][pintdocs] library plus
[currencies](#supported-currencies) and a handful of additional units.

You can [your own custom units](#adding-custom-units) to the workflow. If youthink they'd be useful to everyone, please create a corresponding
[GitHub issue][ghissues] to request addition as a default unit or submit a
[pull request][ghpulls].


### Supported currencies ###

To convert, use the appropriate **abbreviation** for the relevant currencies.

You can also view (and search) the list from within Alfred using the keyword `convcurrencies`.

| Abbreviation |                           Name                           |
|--------------|----------------------------------------------------------|
| AED          | United Arab Emirates Dirham                              |
| AFN          | Afghanistan Afghani                                      |
| ALL          | Albania Lek                                              |
| AMD          | Armenia Dram                                             |
| ANG          | Netherlands Antilles Guilder                             |
| AOA          | Angola Kwanza                                            |
| ARS          | Argentina Peso                                           |
| AUD          | Australia Dollar                                         |
| AWG          | Aruba Guilder                                            |
| AZN          | Azerbaijan New Manat                                     |
| BAM          | Bosnia and Herzegovina Convertible Marka                 |
| BBD          | Barbados Dollar                                          |
| BDT          | Bangladesh Taka                                          |
| BGN          | Bulgaria Lev                                             |
| BHD          | Bahrain Dinar                                            |
| BIF          | Burundi Franc                                            |
| BMD          | Bermuda Dollar                                           |
| BND          | Brunei Darussalam Dollar                                 |
| BOB          | Bolivia Boliviano                                        |
| BRL          | Brazil Real                                              |
| BSD          | Bahamas Dollar                                           |
| BTN          | Bhutan Ngultrum                                          |
| BWP          | Botswana Pula                                            |
| BYR          | Belarus Ruble                                            |
| BZD          | Belize Dollar                                            |
| CAD          | Canada Dollar                                            |
| CDF          | Congo/Kinshasa Franc                                     |
| CHF          | Switzerland Franc                                        |
| CLP          | Chile Peso                                               |
| CNY          | China Yuan Renminbi                                      |
| COP          | Colombia Peso                                            |
| CRC          | Costa Rica Colon                                         |
| CUP          | Cuba Peso                                                |
| CVE          | Cape Verde Escudo                                        |
| CZK          | Czech Republic Koruna                                    |
| DJF          | Djibouti Franc                                           |
| DKK          | Denmark Krone                                            |
| DOP          | Dominican Republic Peso                                  |
| DZD          | Algeria Dinar                                            |
| EGP          | Egypt Pound                                              |
| ERN          | Eritrea Nakfa                                            |
| ETB          | Ethiopia Birr                                            |
| EUR          | Euro Member Countries                                    |
| FJD          | Fiji Dollar                                              |
| FKP          | Falkland Islands (Malvinas) Pound                        |
| GBP          | United Kingdom Pound                                     |
| GEL          | Georgia Lari                                             |
| GHS          | Ghana Cedi                                               |
| GIP          | Gibraltar Pound                                          |
| GMD          | Gambia Dalasi                                            |
| GNF          | Guinea Franc                                             |
| GTQ          | Guatemala Quetzal                                        |
| GYD          | Guyana Dollar                                            |
| HKD          | Hong Kong Dollar                                         |
| HNL          | Honduras Lempira                                         |
| HRK          | Croatia Kuna                                             |
| HTG          | Haiti Gourde                                             |
| HUF          | Hungary Forint                                           |
| IDR          | Indonesia Rupiah                                         |
| ILS          | Israel Shekel                                            |
| INR          | India Rupee                                              |
| IQD          | Iraq Dinar                                               |
| IRR          | Iran Rial                                                |
| ISK          | Iceland Krona                                            |
| JMD          | Jamaica Dollar                                           |
| JOD          | Jordan Dinar                                             |
| JPY          | Japan Yen                                                |
| KES          | Kenya Shilling                                           |
| KGS          | Kyrgyzstan Som                                           |
| KHR          | Cambodia Riel                                            |
| KMF          | Comoros Franc                                            |
| KPW          | Korea (North) Won                                        |
| KRW          | Korea (South) Won                                        |
| KWD          | Kuwait Dinar                                             |
| KYD          | Cayman Islands Dollar                                    |
| KZT          | Kazakhstan Tenge                                         |
| LAK          | Laos Kip                                                 |
| LBP          | Lebanon Pound                                            |
| LKR          | Sri Lanka Rupee                                          |
| LRD          | Liberia Dollar                                           |
| LSL          | Lesotho Loti                                             |
| LTL          | Lithuania Litas                                          |
| LYD          | Libya Dinar                                              |
| MAD          | Morocco Dirham                                           |
| MDL          | Moldova Leu                                              |
| MGA          | Madagascar Ariary                                        |
| MKD          | Macedonia Denar                                          |
| MMK          | Myanmar (Burma) Kyat                                     |
| MNT          | Mongolia Tughrik                                         |
| MOP          | Macau Pataca                                             |
| MRO          | Mauritania Ouguiya                                       |
| MUR          | Mauritius Rupee                                          |
| MVR          | Maldives (Maldive Islands) Rufiyaa                       |
| MWK          | Malawi Kwacha                                            |
| MXN          | Mexico Peso                                              |
| MYR          | Malaysia Ringgit                                         |
| MZN          | Mozambique Metical                                       |
| NAD          | Namibia Dollar                                           |
| NGN          | Nigeria Naira                                            |
| NIO          | Nicaragua Cordoba                                        |
| NOK          | Norway Krone                                             |
| NPR          | Nepal Rupee                                              |
| NZD          | New Zealand Dollar                                       |
| OMR          | Oman Rial                                                |
| PAB          | Panama Balboa                                            |
| PEN          | Peru Nuevo Sol                                           |
| PGK          | Papua New Guinea Kina                                    |
| PHP          | Philippines Peso                                         |
| PKR          | Pakistan Rupee                                           |
| PLN          | Poland Zloty                                             |
| PYG          | Paraguay Guarani                                         |
| QAR          | Qatar Riyal                                              |
| RON          | Romania New Leu                                          |
| RSD          | Serbia Dinar                                             |
| RUB          | Russia Ruble                                             |
| RWF          | Rwanda Franc                                             |
| SAR          | Saudi Arabia Riyal                                       |
| SBD          | Solomon Islands Dollar                                   |
| SCR          | Seychelles Rupee                                         |
| SDG          | Sudan Pound                                              |
| SEK          | Sweden Krona                                             |
| SGD          | Singapore Dollar                                         |
| SHP          | Saint Helena Pound                                       |
| SLL          | Sierra Leone Leone                                       |
| SOS          | Somalia Shilling                                         |
| SRD          | Suriname Dollar                                          |
| STD          | São Tomé and Príncipe Dobra                              |
| SVC          | El Salvador Colon                                        |
| SYP          | Syria Pound                                              |
| SZL          | Swaziland Lilangeni                                      |
| THB          | Thailand Baht                                            |
| TJS          | Tajikistan Somoni                                        |
| TMT          | Turkmenistan Manat                                       |
| TND          | Tunisia Dinar                                            |
| TOP          | Tonga Pa'anga                                            |
| TRY          | Turkey Lira                                              |
| TTD          | Trinidad and Tobago Dollar                               |
| TWD          | Taiwan New Dollar                                        |
| TZS          | Tanzania Shilling                                        |
| UAH          | Ukraine Hryvnia                                          |
| UGX          | Uganda Shilling                                          |
| USD          | United States Dollar                                     |
| UYU          | Uruguay Peso                                             |
| UZS          | Uzbekistan Som                                           |
| VEF          | Venezuela Bolivar                                        |
| VND          | Viet Nam Dong                                            |
| VUV          | Vanuatu Vatu                                             |
| WST          | Samoa Tala                                               |
| XAF          | Communauté Financière Africaine (BEAC) CFA Franc BEAC    |
| XCD          | East Caribbean Dollar                                    |
| XDR          | International Monetary Fund (IMF) Special Drawing Rights |
| XOF          | Communauté Financière Africaine (BCEAO) Franc            |
| XPF          | Comptoirs Français du Pacifique (CFP) Franc              |
| YER          | Yemen Rial                                               |
| ZAR          | South Africa Rand                                        |
| ZMW          | Zambia Kwacha                                            |

### Adding custom units ###

You can add your own custom units using the
[format defined by Pint][pinthowto]. Add your definitions to the
`unit_definitions.txt` file in the workflow's data directory.

To edit this file, enter `convinfo` in Alfred and select `Edit Custom Units`.
The `unit_definitions.txt` file will open in your default text editor.

Please see the [Pint documentation][pinthowto] for the required format. See
Pint's [default unit definitions][pintunits] for examples.

## Thanks, copyright, licensing ##

- The Python [Pint][pintdocs] library does all the heavy lifting. See the [Pint GitHub repo][pintrepo] for Pint licensing or `LICENSE.txt` and `AUTHORS.txt` in the `pint` subdirectory.
- The money icon is from [Gettyicons.com][getty] and was created by
[DaPino][dapino].
- The workflow icon is from [Font Awesome][fontawesome]
- Exchange rates are downloaded from the [Yahoo! Finance][yahoo-finance].
- The [Alfred-Workflow][alfred-workflow] library is used heavily.

All other code/media are released under the [MIT Licence](http://opensource.org/licenses/MIT).

[pintdocs]: http://pint.readthedocs.org/en/latest/index.html
[pintrepo]: https://github.com/hgrecco/pint
[pinthowto]: http://pint.readthedocs.org/en/latest/defining.html
[pintunits]: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
[ghissues]: https://github.com/deanishe/alfred-convert/issues
[ghpulls]: https://github.com/deanishe/alfred-convert/pulls
[ghreleases]: https://github.com/deanishe/alfred-convert/releases
[packal]: http://www.packal.org/workflow/convert
[yahoo-finance]: http://finance.yahoo.com/
[getty]: http://www.gettyicons.com/free-icon/105/money-icon-set/free-money-icon-png/
[dapino]: http://www.dapino-colada.nl/
[fontawesome]: http://fortawesome.github.io/Font-Awesome/
[alfred-workflow]: http://www.deanishe.net/alfred-workflow/
[alfred]: http://www.alfredapp.com/
[demo]: https://raw.github.com/deanishe/alfred-convert/master/demo.gif
