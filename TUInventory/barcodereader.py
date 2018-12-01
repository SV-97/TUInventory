# from argparse import ArgumentParser
from collections import Counter
from time import sleep
from sys import stderr
import threading

import cv2
import numpy as np
from pyzbar import pyzbar

# from virtualkeyboard import VirtualKeyboard
# from systemmetrics import SystemMetrics

"""
parser = ArgumentParser(description="Get barcode from video feed")
parser.add_argument("-c", "--camera_id", dest="camera_id", default=0, type=int, help="ID for the video feed (default: use standart camera)")
parser.add_argument("-da", "--disable_abort", dest="disable_abort", action="store_true", help="Disable closing the videofeed with esc or lmb (WARNING: Has to be killed if no code is found) (default: don't abort it)")
parser.add_argument("-m", "--mirror", dest="mirror", action="store_true", help="Invert video feed, along y-axis")
parser.add_argument("-f", "--fullscreen", dest="fullscreen", action="store_true", help="Display fullscreen if true else display window")
args = parser.parse_args()
camera_id = args.camera_id
disable_abort = args.disable_abort
mirror = args.mirror
fullscreen = args.fullscreen
"""

class VideoStream(threading.Thread):
    """Class for reading barcodes of all kinds from a video feed and marking them in the image
    """
    def __init__(self, target_resolution=None, camera_id=0):
        super().__init__()
        self.camera = Camera(camera_id)
        self._frame = None
        self._barcodes = None
        self._mirror = False
        self._abort = False
        self.frame_lock = threading.Lock()
        self.barcode_lock = threading.Lock()
        self.gp_lock = threading.Lock()
        self._target_resolution = target_resolution # (width, height)

    def _set_frame(self, frame):
        with self.frame_lock:
            self._frame = frame

    def _get_frame(self):
        with self.frame_lock:
            frame = self.frame
        if self.mirror:
            frame = cv2.flip(frame, 1)
        if self.target_resolution:
            frame = cv2.resize(frame, (self.target_resolution[0], self.target_resolution[1]))
        return frame

    def _set_barcodes(self, barcode):
        with self.barcode_lock:
            self._barcode = barcode

    def _get_barcodes(self):
        with self.barcode_lock:
            return self._barcode

    def _set_mirror(self, mirror):
        with self.gp_lock:
            self._mirror = mirror

    def _get_mirror(self):
        with self.gp_lock:
            return self._mirror

    def _set_abort(self, abort):
        with self.gp_lock:
            self._abort = abort

    def _get_abort(self):
        with self.gp_lock:
            return self._abort

    def _set_target_resolution(self, resolution):
        with self.gp_lock:
            self._target_resolution = resolution

    def _get_target_resolution(self):
        with self.gp_lock:
            return self._target_resolution

    frame = property(fget=_get_frame, fset=_set_frame)
    barcodes = property(fget=_get_barcodes, fset=_set_barcodes)
    mirror = property(fget=_get_mirror, fset=_set_mirror)
    abort = property(fget=_get_abort, fset=_set_abort)
    target_resolution = property(fget=_get_target_resolution, fset=_set_target_resolution)

    @staticmethod
    def rect_transformation(x, y, width, height):
        """Transform rectangle of type "origin + size" to "two-point"
        Args:
            x (int): x coordinate of origin
            y (int): y coordinate of origin
            width (int): width of rectangle
            height (int): height of rectangle
        Returns:
            Tuple of tuple of int with x-y-coordinate pairs for both points
        """
        return ((x, y), (x + width, y + height))

    def find_and_mark_barcodes(self, frame):
        barcodes = pyzbar.decode(frame)
        found_codes = []
        for barcode in barcodes:
            barcode_information = (barcode.type, barcode.data.decode("utf-8"))
            if barcode_information not in found_codes:
                found_codes.append(barcode_information)
            poly = barcode.polygon
            poly = np.asarray([(point.x, point.y) for point in poly])
            poly = poly.reshape((-1,1,2))
            cv2.polylines(frame, [poly] ,True, (0,255,0), 2)
            cv2.rectangle(frame, *self.rect_transformation(*barcode.rect), (255, 0, 0), 2)
            x, y = barcode.rect[:2]
            cv2.putText(frame, "{}({})".format(*barcode_information), (x, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
        return frame, found_codes

    def run(self):
        while not self.abort:
            with self.camera as camera:
                frame = camera.read()[1]
            marked_frame, found_codes = self.find_and_mark_barcodes(frame)
            self.frame = marked_frame
            self.barcodes = found_codes



class CantOpenCameraException(Exception):
    def __init__(self, camera_id):
        super().__init__(self)
        self.text = f"Unable to open Camera {camera_id}"


class Camera():
    """Context Manager for video streams"""
    def __init__(self, camera_id=0):
        self.camera_id = camera_id

    def __enter__(self):
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            raise CantOpenCameraException(self.camera_id)
        return self.camera

    def __exit__(self, exc_type, exc_value, traceback):
        self.camera.release()

