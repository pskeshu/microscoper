# Microscoper

Microscoper is a simple wrapper for `python-bioformats`, with added features, such as saving images based on the filters used while acquiring them (For example: DAPI.tif for a Z stack of images acquired using the DAPI channel).

## Installation

### python-bioformats

This package requires a forked `python-bioformats` from `pskeshu/python-bioformats`.

This can be installed directly with `pip`, and this is an essential step before installing `microscoper`.

    pip install git+http://github.com/pskeshu/python-bioformats.git@1.1.0s#egg=python-bioformats-1.1.0s

You can also install the forked `python-bioformats` by cloning the repository from github.

    git clone https://github.com/pskeshu/python-bioformats.git
    cd python-bioformats
    git checkout scblab
    python setup.py install
    
### microscoper

To install `microscoper` with `pip`

    pip install microscoper

Or install the latest development version from github:

    git clone https://github.com/pskeshu/microscoper.git
    cd microscoper
    pip install -e .


## Usage

Navigate to any folder which has microscope images in bioformats supported format, and in the terminal run the following command:

    python -m microscoper -f . -k .vsi

The `-f path/to/images` flag specifies the directory in which to look for files that have the keyword specified by `-k .vsi`. By default, `-f` looks into all directories under the specified directory. So, if you have a directory structure like this:

    |-cells
    |---control
    |-----image_1.vsi
    |-----image_2.vsi
    |-----40X
    |-------image_3.vsi
    |---treatment
    |-----image_1.vsi
    |-----image_2.vsi

If you input `python -m microscoper -f cells/`, all the images in the subdirectories will be taken as the input. Note that the `-k` argument is optional if you're working with .vsi files, as it takes `-k .vsi` by default. 

The defaults for `-f` is `.` or the current directory. If the working directory is `/home/user/data/exp/cells` for the directory tree given above, running `python -m microscoper` alone is sufficient.

In case you want to make sure the right files are being converted, you can initiate a dry run by passing an addition `--list` argument. For the above directory tree, the dry run will return something like this:
    
    $ pwd
        /home/user/data/exp/cells
    
    $ python -m microscoper --list
        ./control/40X/image_3.vsi
        ./control/image_1.vsi
        ./control/image_2.vsi
        ./treatment/image_1.vsi
        ./treatment/image_2.vsi
        ======================
        Total files found: 5
        ======================

Dry run will exit without converting the supported files to TIFF.

## Note

This program has only been tested with Olympus CellSense format, .vsi, but can potentially be used with any bioformats supported file format. Supply the file format with the  `-k` argument.

If you want `microscoper` to work with your favourite proprietary image format, send me a sample image.

## Future Plans

* Input files pattern matching with wildcards and regular expressions.
* Write meta data to text files, or directly to the TIFF files.

## Fork

Feel free to fork this repository to modify the program as you seem fit, or submit push requests.
