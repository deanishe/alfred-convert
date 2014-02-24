# Alfred-Convert #

Convert between different units in [Alfred 2](http://www.alfredapp.com/).

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot1.png "")

Alfred-Convert uses a [built-in library](http://pint.readthedocs.org/en/latest/index.html) to do the conversion offline, so conversions are fast, but currencies are not supported.

## Downloading ##

Download from [GitHub]() or [Packal]().

## Usage ##

The syntax is simple: the quantity, the unit you want to convert from then the unit you want to convert to. For example:

- `conv 128 mph km`
- `conv 72in cm`
- `conv 100psi bar`
- `conv 20.5 m/s mph`

It doesn't matter if there is a space between the quantity and the units or not. Alfred-Convert will tell you if it doesn't understand your query or know the units.

## Screenshots ##

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot1.png "")

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot2.png "")

![](https://raw.github.com/deanishe/alfred-convert/master/screenshot3.png "")

## Thanks, copyright, licensing ##

The Python [Pint](http://pint.readthedocs.org/en/latest/index.html) library does all the heavy lifting. See the [Pint GitHub repo](https://github.com/hgrecco/pint) for Pint licensing or `LICENSE.txt` and `AUTHORS.txt` in the `pint` subdirectory.

All other code/media are released under the [MIT Licence](http://opensource.org/licenses/MIT).
