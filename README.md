tarifas2wiki
============

This little script processes the [Fare Resolution](data/Resolucion_Tarifas_Abril_2017.pdf)
of the Nicaraguan transport ministry to generate tables used on the OSM-Wiki pages to track
the process of the mapping of Nicaraguan public transport routes.

Please make sure you use Python 3 to run it.

Use
------------

* Install dependencies with `pip3 install -r requirements.txt`
* Run `python3 convert.py > output.txt`
* Copy the generated text inside `output.txt` to the wikipages


License
-------

![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)

This program is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
