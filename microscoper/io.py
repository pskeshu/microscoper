"""Microscoper is a wrapper around bioformats using a forked
python-bioformats to extract the raw images from Olympus IX83
CellSense .vsi format, into a more commonly used TIFF format.

Images are bundled together according to their channels.

This code is used internally in SCB Lab, TCIS, TIFR-H.
You're free to modify it and distribute it.
"""
from __future__ import unicode_literals, print_function

import os
import xml.dom.minidom

import bioformats as bf
import javabridge as jb
import numpy as np
import tifffile as tf
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
    meta = bf.get_omexml_metadata(filename)
    metadata = bf.omexml.OMEXML(meta)
    return metadata


def get_channel(metadata, channel):
    """Return the channel name from the metadata object"""
    try:
        channel_name = metadata.image().Pixels.Channel(channel).Name
    except AttributeError:
        return

    if channel_name is None:
        return
    return channel_name.replace("/", "_")


def read_images(path, save_directory, big, save_separate):
    """Reads images from the .vsi and associated files.
    Returns a dictionary with key as channel, and list
    of images as values."""
    with bf.ImageReader(path) as reader:
        # Shape of the data
        c_total = reader.rdr.getSizeC()
        z_total = reader.rdr.getSizeZ()
        t_total = reader.rdr.getSizeT()

        # Since we don't support hyperstacks yet...
        if 1 not in [z_total, t_total]:
            raise TypeError("Only 4D images are currently supported.")

        metadata = get_metadata(path)

        # This is so we can manually set a description down below.
        pbar_c = tqdm.tqdm(range(c_total))

        for channel in pbar_c:
            images = []
            # Get the channel name, so we can name the file after this.
            channel_name = get_channel(metadata, channel)

            # Update the channel progress bar description with the
            # channel name.
            pbar_c.set_description(channel_name)

            for time in tqdm.tqdm(range(t_total), "T"):
                for z in tqdm.tqdm(range(z_total), "Z"):
                    image = reader.read(c=channel,
                                        z=z,
                                        t=time,
                                        rescale=False)

                    # If there's no metadata on channel name, save channels
                    # with numbers,starting from 0.
                    if channel_name is None:
                        channel_name = str(channel)

                    images.append(image)

            save_images(np.asarray(images), channel_name, save_directory, big,
                        save_separate)

    return metadata


def save_images(images, channel, save_directory, big=False,
                save_separate=False):
    """Saves the images as TIFs with channel name as the filename.
    Channel names are saved as numbers when names are not available."""

    # Make the output directory, if it doesn't alredy exist.
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Save a file for every image in a stack.
    if save_separate:
        filename = save_directory + str(channel) + "_{}.tif"
        for num, image in enumerate(images):
            with tf.TiffWriter(filename.format(num + 1), bigtiff=big) as f:
                f.write(image)

    # Save a single .tif file for all the images in a channel.
    else:
        filename = save_directory + str(channel) + ".tif"
        with tf.TiffWriter(filename, bigtiff=big) as f:
            f.write(images)


def save_metadata(metadata, save_directory):
    data = xml.dom.minidom.parseString(metadata.to_xml())
    pretty_xml_as_string = data.toprettyxml()

    with open(save_directory + "metadata.xml", "w") as xmlfile:
        xmlfile.write(pretty_xml_as_string)


def _init_logger():
    """This is so that Javabridge doesn't spill out a lot of DEBUG messages
    during runtime.
    From CellProfiler/python-bioformats.
    """
    rootLoggerName = jb.get_static_field("org/slf4j/Logger",
                                         "ROOT_LOGGER_NAME",
                                         "Ljava/lang/String;")

    rootLogger = jb.static_call("org/slf4j/LoggerFactory",
                                "getLogger",
                                "(Ljava/lang/String;)Lorg/slf4j/Logger;",
                                rootLoggerName)

    logLevel = jb.get_static_field("ch/qos/logback/classic/Level",
                                   "WARN",
                                   "Lch/qos/logback/classic/Level;")

    jb.call(rootLogger,
            "setLevel",
            "(Lch/qos/logback/classic/Level;)V",
            logLevel)


def run():
    # Add file extensions to this to be able to read different file types.
    extensions = [".vsi"]

    arg = arguments()
    files = get_files(arg.f, arg.k)

    if 0 == len(files):
        print("No file matching *{}* keyword.".format(arg.k))
        exit()

    if arg.list:
        for f in files:
            print(f)
        print("======================")
        print("Total files found:", len(files))
        print("======================")
        exit()

    jb.start_vm(class_path=bf.JARS, max_heap_size=arg.m)

    pbar_files = tqdm.tqdm(files)

    for path in pbar_files:
        if not any(_ in path for _ in extensions):
            continue

        file_location = os.path.dirname(os.path.realpath(path))
        filename = os.path.splitext(os.path.basename(path))[0]
        save_directory = file_location + "/_{}_/".format(filename)

        pbar_files.set_description("..." + path[-15:])

        # If the user wants to store meta data for existing data,
        # the user may pass -om or --onlymetadata argument which
        # will bypass read_images() and get metadata on its own.

        if arg.onlymetadata:
            metadata = get_metadata(path)

        # The default behaviour is to store the files with the
        # metadata.
        else:
            metadata = read_images(path, save_directory, big=arg.big,
                                   save_separate=arg.separate)

        save_metadata(metadata, save_directory)

    jb.kill_vm()
