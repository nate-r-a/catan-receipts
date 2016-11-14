# Catan Receipts
A Python script that pulls data from Google Sheets, formats it, and inserts it into custom-made HTML and CSS for printing with [Adafruit's Mini Thermal Receipt Printer](https://www.adafruit.com/products/597). The structure of the main file is directly based on my own Google Sheet that contains all of the data I've collected from Settlers of Catan plays, as seen [here](http://bit.ly/FederationOfCatan2).

Printing is done on a Raspberry Pi 3 using CUPS with [klirichek's zj-58 filter](https://github.com/klirichek/zj-58). An example receipt image from game #75 can be seen above.

### Dependencies
The data extraction from Google Sheets is done using [gspread](https://github.com/burnash/gspread), and the graphs are created using [Plotly](https://plot.ly/). Conversion of the created webpage to bitmap is done using [wkhtmltoimage](http://wkhtmltopdf.org/) and Python Imaging Library.
