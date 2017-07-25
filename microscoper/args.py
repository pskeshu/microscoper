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
    parser.add_argument("--list",
                        help="Show files that are to be opened,\
                        without opening them.",
                        action="store_true")
    args = parser.parse_args()
    return args
