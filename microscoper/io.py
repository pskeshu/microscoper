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
import tqdm
from .args import arguments


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
    return sorted(file_list)


def get_metadata(filename):
    """Read the meta data and return the metadata object.
    """
    meta = bioformats.get_omexml_metadata(filename)
    meta.encode("utf8")  # Python2 support
    metadata = bioformats.omexml.OMEXML(meta)
    return metadata


def get_channel(metadata, channel):
    """Return the channel name from the metadata object"""
    try:
        channel_name = metadata.image().Pixels.Channel(channel).Name
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

        c_total = reader.rdr.getSizeC()
        z_total = reader.rdr.getSizeZ()
        t_total = reader.rdr.getSizeT()

        if 1 not in [z_total, t_total]:
            raise TypeError("Only 4D images are currently supported.")

        metadata = get_metadata(path)

        for channel in tqdm.tqdm(range(c_total), "C"):
            channel_name = get_channel(metadata, channel)
            for time in tqdm.tqdm(range(t_total), "T"):
                for z in tqdm.tqdm(range(z_total), "Z"):
                    image = reader.read(c=channel,
                                        z=z,
                                        t=time,
                                        rescale=False)

                    if channel_name is None:
                        channel_name = str(channel)
                    images[channel_name].append(image)

    for lists in images:
        images[lists] = np.asarray(images[lists])

    return images


def save_images(images, save_directory, bigtiff=False):
    """Saves the images as TIFs with channel numbers
    as the filename."""
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    for channel in images:
        filename = save_directory+"/"+str(channel)+".tif"
        with tifffile.TiffWriter(filename, bigtiff=bigtiff) as tif:
            tif.save(images[channel])


def init_logger():
    rootLoggerName = javabridge.get_static_field("org/slf4j/Logger",
                                                 "ROOT_LOGGER_NAME", "Ljava/lang/String;")
    rootLogger = javabridge.static_call("org/slf4j/LoggerFactory",
                                        "getLogger", "(Ljava/lang/String;)Lorg/slf4j/Logger;", rootLoggerName)
    logLevel = javabridge.get_static_field("ch/qos/logback/classic/Level",
                                           "WARN", "Lch/qos/logback/classic/Level;")
    javabridge.call(rootLogger, "setLevel", "(Lch/qos/logback/classic/Level;)V",
                    logLevel)


def run():
    a = arguments()
    files = get_files(a.f, a.k)

    if 0 == len(files):
        print("No {} file found.".format(a.k))
        exit()

    if a.list:
        for f in files:
            print(f)
        print("======================")
        print("Total files found:", len(files))
        print("======================")
        exit()

    javabridge.start_vm(class_path=bioformats.JARS, max_heap_size="2G")

    init_logger()

    for path in tqdm.tqdm(files):
        file_location = os.path.dirname(os.path.realpath(path))
        filename = path.split("/")[-1].split(".vsi")[0]
        filename = "_%s_" % (filename)
        save_directory = "%s/%s" % (file_location, filename)
        images = read_images(path)
        save_images(images, save_directory)
    javabridge.kill_vm()
