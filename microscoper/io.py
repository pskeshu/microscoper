"""Microscoper is a wrapper around bioformats using a forked 
python-bioformats to extract the raw images from Olympus IX83 
CellSense .vsi format, into a more commonly used TIFF format.

Images are bundled together according to their channels. 

This code is used internally in SCB Lab, TCIS, TIFR-H.
You're free to modify it and distribute it.
"""
from __future__ import unicode_literals, print_function
import os
import collections
import bioformats
import javabridge
import numpy as np
import tifffile


def get_files(directory, keyword):
    """ Returns all the files in the given directory 
    and subdirectories, filtering with the keyword.

    Usage:
        >>> all_vsi_files = get_files(".", ".vsi")

        This will have all the .vsi files in the current
        directory and all other directories in the current
        directory.
    """
    file_list = []
    for path, subdirs, files in os.walk(directory):
        for name in files:
            filename = os.path.join(path, name)
            if keyword in filename:
                file_list.append(filename)
    return file_list


def get_channel(filename, channel):
    """Read the meta data and return the channel name/filter
    name for a certain int channel.
    """
    meta = bioformats.get_omexml_metadata(filename)
    o = bioformats.omexml.OMEXML(meta)

    try:
        channel_name = o.image().Pixels.Channel(channel).Name
    except:
        return

    if channel_name is None:
        return
    return channel_name.replace("/", "_")


def read_images(path):
    """Reads images from the .vsi and associated files.
    Returns a dictionary with key as channel, and list
    of images as values."""
    with bioformats.ImageReader(path) as reader:
        images = collections.defaultdict(list)
        z_total = reader.rdr.getSizeZ()
        c_total = reader.rdr.getSizeC()
        t_total = reader.rdr.getSizeT()
        for time in xrange(t_total):
            for z in xrange(z_total):
                for channel in xrange(c_total):
                    image = reader.read(c=channel,
                                        z=z, t=time, rescale=False)
                    channel_name = get_channel(path, channel)
                    if channel_name is None:
                        channel_name = str(channel)
                    images[channel_name].append(image)
    for lists in images:
        images[lists] = numpy.asarray(images[lists])
    return images


def save_images(images, save_directory):
    """Saves the images as TIFs with channel numbers
    as the filename."""
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    for channel in images:
        with tifffile.TiffWriter(save_directory+"/"+str(channel)+".tif",
                                 bigtiff=False) as tif:
            tif.save(images[channel])

if __name__ == "__main__":

    files = get_files(".", ".vsi")

    if 0 == len(files):
        print "No .vsi files found."

    else:
        javabridge.start_vm(class_path=bioformats.JARS, run_headless=True)
        for path in files:
            file_location = os.path.dirname(os.path.realpath(path))
            filename = path.split("/")[-1].split(".vsi")[0]
            filename = "_%s_" % (filename)
            save_directory = "%s/%s" % (file_location, filename)
            images = read_images(path)
            save_images(images, save_directory)
        javabridge.kill_vm()
