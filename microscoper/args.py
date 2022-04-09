import argparse


def arguments():
    des = "Microscopy image file format converter.\
    Converts .vsi and other formats to TIFF."
    parser = argparse.ArgumentParser(description=des,
                                     prog="python -m microscoper")
    parser.add_argument("-f",
                        help="The folder in which to look for images.",
                        default="./")
    parser.add_argument("-k",
                        help="Image keyword",
                        default=".vsi")
    parser.add_argument("-m",
                        "--memory",
                        help="Set the memory limit for Java to use. E.g. -m 8G",
                        default="2G")
    parser.add_argument("--list",
                        help="Show files that are to be opened,\
                        without opening them.",
                        action="store_true")
    parser.add_argument("-s",
                        "--separate",
                        help="Images from the same channel won't\
                        be grouped as stacks.",
                        action="store_true")
    parser.add_argument("-b",
                        "--big",
                        help="Save as big TIFF",
                        action="store_true")
    parser.add_argument("-om",
                        "--onlymetadata",
                        help="Read and save the metadata without\
                        saving the images.",
                        action="store_true")

    args = parser.parse_args()
    return args
