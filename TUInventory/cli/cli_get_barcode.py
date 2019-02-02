"""Simple barcodereader command line interface"""

from argparse import ArgumentParser
from sys import exit, stderr, stdout

parser = ArgumentParser(description="Extract all barcodes from an image")
parser.add_argument("-i", "--image", dest="path", type=str, help="Path to image")
parser.add_argument("-d", "--detailed", dest="detailed", action="store_true", help="Return all extracted information")
parser.add_argument("-tb", "--enable_tracebacks", dest="enable_tracebacks", action="store_true", help="Enable tracebacks rather than custom messages")

args = parser.parse_args()
path = args.path
detailed = args.detailed
enable_tracebacks = args.enable_tracebacks

try:
    from cv2 import imread
except ImportError as e:
    if enable_tracebacks:
        raise e
    exit("Failed to import OpenCV (Module cv2)")
try:
    from pyzbar import pyzbar
except ImportError as e:
    if enable_tracebacks:
        raise e
    exit("Failed to import pyzbar")


if not path:
    stderr.write("No path provided\n")
    exit(1)

try:
    image = imread(path)
    barcodes = pyzbar.decode(image)
    if not barcodes:
        stderr.write("Couldn't find any barcodes\n")
        exit(1)
except TypeError as e:
    if enable_tracebacks:
        raise e
    stderr.write(f"There's no valid image at {path}\n")
    exit(1)


if detailed:
    stdout.write(str(barcodes))
else:
    stdout.write(barcodes[0].data.decode("utf-8"))
exit(0)