
# Alfred-Convert #

Convert between different units offline in [Alfred 2 & 3][alfred].

![][demo]

Alfred-Convert uses a [built-in library][pintdocs] for lightning fast conversions.

You can also add your own custom units.

**Note:** Currency conversions do require occasional Internet connectivity to update exchange rates. Alfred-Convert will otherwise work just fine without an Internet connection.

- [Downloading](#downloading)
- [Usage](#usage)
- [Supported units](#supported-units)
    - [Supported currencies](#supported-currencies)
    - [Adding custom units](#adding-custom-units)
- [Releases](#releases)
- [Thanks, copyright, licensing](#thanks-copyright-licensing)


## Downloading ##

Download from [GitHub][ghreleases] or [Packal.org][packal].


## Usage ##


### Conversions ###

The syntax is simple: the quantity, the unit you want to convert from then the unit you want to convert to. For example:

- `conv 128 mph kph`
- `conv 72in cm`
- `conv 100psi bar`
- `conv 20.5 m/s mph`
- `conv 100 eur gbp`

It doesn't matter if there is a space between the quantity and the units or not. Alfred-Convert will tell you if it doesn't understand your query or know the units.

Actioning an item (selecting it and hitting `↩`) will copy it to the clipboard. Using `⌘+L` will display the result in Alfred's large text window, `⌘+C` will copy the selected result to the clipboard.


### Settings ###

Use `convinfo` to view the built-in help file, view/search the list of
supported currencies, change the number of decimal places shown in conversions, or edit your custom units.


### Custom units ###

See [Adding custom units](#adding-custom-units).


## Supported units ##

Currently, Alfred-Convert only supports [the units][pintunits] understood by the underlying [Pint][pintdocs] library plus [currencies](#supported-currencies) and a handful of additional units.

You can [your own custom units](#adding-custom-units) to the workflow. If you think they'd be useful to everyone, please create a corresponding [GitHub issue][ghissues] to request addition as a default unit or submit a [pull request][ghpulls].


### Supported currencies ###

To convert, use the appropriate **abbreviation** for the relevant currencies, e.g. `conv 100 eur gbp`.

You can also view (and search) the list from within Alfred by using the keyword `convinfo` and choosing `View Supported Currencies`.

[All supported currencies](./docs/currencies.md).


### Adding custom units ###

You can add your own custom units using the [format defined by Pint][pinthowto]. Add your definitions to the `unit_definitions.txt` file in the workflow's data directory.

To edit this file, enter `convinfo` in Alfred and select `Edit Custom Units`. The `unit_definitions.txt` file will open in your default text editor.

Please see the [Pint documentation][pinthowto] for the required format. See Pint's [default unit definitions][pintunits] for examples.


## Releases ##

See [CHANGELOG][changelog] for more information.

|   Release   |      Date      |
|-------------|----------------|
| [2.4][v2.4] | 2015-11-28     |
| [2.3][v2.3] | 2015-11-26     |
| [2.2][v2.2] | 2015-07-16     |
| 2.1         | Never released |
| [2.0][v2.0] | 2014-12-26     |
| [1.2][v1.2] | 2014-08-19     |
| [1.1][v1.1] | 2014-08-09     |


## Thanks, copyright, licensing ##

- The Python [Pint][pintdocs] library does all the heavy lifting. See the [Pint GitHub repo][pintrepo] for Pint licensing or `LICENSE.txt` and `AUTHORS.txt` in the `vendor/pint` subdirectory.
- The workflow icons are from [Font Awesome][fontawesome]
- Exchange rates are downloaded from the [Yahoo! Finance][yahoo-finance].
- The [Alfred-Workflow][alfred-workflow] library is used heavily.

All other code/media are released under the [MIT Licence](http://opensource.org/licenses/MIT).


[alfred-workflow]: http://www.deanishe.net/alfred-workflow/
[alfred]: http://www.alfredapp.com/
[changelog]: ./CHANGELOG.md
[demo]: https://raw.github.com/deanishe/alfred-convert/master/demo.gif
[fontawesome]: http://fortawesome.github.io/Font-Awesome/
[ghissues]: https://github.com/deanishe/alfred-convert/issues
[ghpulls]: https://github.com/deanishe/alfred-convert/pulls
[ghreleases]: https://github.com/deanishe/alfred-convert/releases
[packal]: http://www.packal.org/workflow/convert
[pintdocs]: http://pint.readthedocs.org/en/latest/index.html
[pinthowto]: http://pint.readthedocs.org/en/latest/defining.html
[pintrepo]: https://github.com/hgrecco/pint
[pintunits]: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
[v1.1]: https://github.com/deanishe/alfred-convert/releases/tag/v1.1
[v1.2]: https://github.com/deanishe/alfred-convert/releases/tag/v1.2
[v2.0]: https://github.com/deanishe/alfred-convert/releases/tag/v2.0
[v2.2.1]: https://github.com/deanishe/alfred-convert/releases/tag/v2.2.1
[v2.2]: https://github.com/deanishe/alfred-convert/releases/tag/v2.2
[v2.3]: https://github.com/deanishe/alfred-convert/releases/tag/v2.3
[v2.4]: https://github.com/deanishe/alfred-convert/releases/tag/v2.4
[yahoo-finance]: https://finance.yahoo.com/
