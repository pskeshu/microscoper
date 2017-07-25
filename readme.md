Microscoper
===========

Microscoper is a simple wrapper for `python-bioformats`, with added features, such as saving images based on the filters used while acquiring them (For example: DAPI.tif for a Z stack of images acquired using the DAPI channel).

To install the package with pip

`pip install microscoper`

Or install from the latest development repository:

`git clone https://github.com/pskeshu/microscoper.git`
`cd microscoper`
`pip install -e .`


Usage
-----



Navigate to any folder which has microscope images in bioformats supported format, and in the terminal run the following command:

`python -m microscoper -f . -k .vsi`

This program has only been tested with Olympus CellSense format, .vsi, but can potentially be used with any bioformats supported file format. Supply the file format with the  `-k` argument.

Fork
----

Feel free to fork this repository to modify the program as you seem fit, or submit push requests.