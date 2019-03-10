"""Allows opening a camera feed and finding barcodes in it"""

from collections import Counter
from time import sleep
from sys import platform, stderr
import threading
import queue

import cv2
import numpy as np
from pyzbar import pyzbar

from utils import parallel_print


class VideoStream(threading.Thread):
    """Class for reading barcodes of all kinds from a video feed and marking them in the image
    Be sure you can't use the LazyVideoStream instead!
    """
    def __init__(self, target_resolution=None, camera_id=0):
        """
        Args:
            target_resolution: Tuple of (width, height) to set the final resolution of the frames
            camera_id: The id of the camera that's to be used (if your system only has one it's zero)
        """
        super().__init__(name=f"{self.__class__.__name__}Thread_{camera_id}")
        self.camera = Camera(camera_id)
        self.camera_id = camera_id
        self.barcodes = []
        self._mirror = False
        self._abort = False
        self.frame_lock = threading.Lock()
        self.gp_lock = threading.Lock()
        self._target_resolution = target_resolution
        self._frame = np.zeros((1, 1))

    def _set_frame(self, frame):
        with self.frame_lock:
            self._frame = frame

    def _get_frame(self):
        with self.frame_lock:
            frame = self._frame
        if self.mirror:
            frame = cv2.flip(frame, 1)
        if self.target_resolution:
            frame = cv2.resize(frame, (self.target_resolution[0], self.target_resolution[1]))
        return frame

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
        """Find barcodes in given frame
            Args:
                frame: Frame that barcodes are to be detected in
            Returns: 
                Tuple of frame where barcodes are marked, list of all found codes in frame
        """
        barcodes = pyzbar.decode(frame)
        found_codes = []
        for barcode in barcodes:
            barcode_information = (barcode.type, barcode.data.decode("utf-8"))
            if barcode_information not in found_codes:
                found_codes.append(barcode_information)
            poly = barcode.polygon
            poly = np.asarray([(point.x, point.y) for point in poly])
            poly = poly.reshape((-1, 1, 2))
            cv2.polylines(frame, [poly], True, (0, 255, 0), 2)
            cv2.rectangle(frame, *self.rect_transformation(*barcode.rect), (255, 0, 0), 2)
            x, y = barcode.rect[:2]
            cv2.putText(
                frame, 
                "{}({})".format(*barcode_information), 
                (x, y - 10), 
                cv2.FONT_HERSHEY_PLAIN, 
                1, 
                (0, 0, 255), 
                1)
        return frame, found_codes

    def run(self):
        with self.camera as camera:
            while not self.abort:
                frame = camera.read()[1]
                marked_frame, found_codes = self.find_and_mark_barcodes(frame)
                self.frame = marked_frame
                if found_codes:
                    self.barcodes.append(found_codes)


class LazyVideoStream(threading.Thread):
    """Class for reading barcodes of all kinds from a video feed and marking them in the image
    This Lazy implementation only processes frames on demand
    
        Args:
            target_resolution: Tuple of (width, height) to set the final resolution of the frames
            camera_id: The id of the camera that's to be used (if your system only has one it's zero)
        
        Attributes:
            camera: Instance of Camera with for given camera_id
            camera_id: Given camera_id
            _mirror: Set to True to mirror the frame
            gp_lock: general purpose lock for property access
            _target_resolution: Tuple of (width, height) to set the final resolution of the frames
            request_queue: Queue that's used to request a frame, request by putting True
            frame_queue: Queue that answer frames get pushed into
        
        Properties:
            mirror: gp_lock locked _mirror
            target_resolution: gp_lock locked _target_resolution
    """
    def __init__(self, target_resolution=None, camera_id=0):
        super().__init__(name=f"{self.__class__.__name__}Thread_{camera_id}")
        self.camera = Camera(camera_id)
        self.camera_id = camera_id
        self._mirror = False
        self.gp_lock = threading.Lock()
        self._target_resolution = target_resolution # (width, height)
        self.request_queue = queue.Queue()
        self.frame_queue = queue.Queue()
        with self.camera:
            pass

    def _set_mirror(self, mirror):
        with self.gp_lock:
            self._mirror = mirror

    def _get_mirror(self):
        with self.gp_lock:
            return self._mirror

    def _set_target_resolution(self, resolution):
        with self.gp_lock:
            self._target_resolution = resolution

    def _get_target_resolution(self):
        with self.gp_lock:
            return self._target_resolution

    mirror = property(fget=_get_mirror, fset=_set_mirror)
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
        """Find barcodes in given frame
            Args:
                frame: Frame that barcodes are to be detected in
            Returns: 
                Tuple of frame where barcodes are marked, list of all found codes in frame
        """
        barcodes = pyzbar.decode(frame)
        found_codes = []
        for barcode in barcodes:
            barcode_information = (barcode.type, barcode.data.decode("utf-8"))
            if barcode_information not in found_codes:
                found_codes.append(barcode_information)
            poly = barcode.polygon
            poly = np.asarray([(point.x, point.y) for point in poly])
            poly = poly.reshape((-1, 1, 2))
            cv2.polylines(frame, [poly], True, (0, 255, 0), 2)
            # cv2.rectangle(frame, *self.rect_transformation(*barcode.rect), (255, 0, 0), 2)
            x, y = barcode.rect[:2]
            """
            cv2.putText(
                frame, 
                "{}({})".format(*barcode_information), 
                (x, y - 10), 
                cv2.FONT_HERSHEY_PLAIN, 
                1, 
                (0, 0, 255), 
                1)"""
        return frame, found_codes

    def request(self):
        """Convenience function to abstract the request_queue from the user"""
        self.request_queue.put(True)

    def run(self):
        """Start connection to camera and answer requests"""
        with self.camera as camera:
            while True:
                self.request_queue.get()
                frame = camera.read()[1]
                marked_frame, found_codes = self.find_and_mark_barcodes(frame)
                if self.target_resolution:
                    marked_frame = cv2.resize(marked_frame, (self.target_resolution[0], self.target_resolution[1]))
                self.frame = marked_frame
                self.frame_queue.put((frame, found_codes))
                self.request_queue.task_done()


class Camera():
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
    def __enter__(self):
        if "win32" in platform:
            self.camera = cv2.VideoCapture(cv2.CAP_DSHOW + self.camera_id)
        else:
            self.camera = cv2.VideoCapture(self.camera_id)
            
        if not self.camera.isOpened():
            raise IOError(f"Failed to open camera {self.camera_id}")
        while not self.camera.read()[0]:
            pass
        return self.camera
    def __exit__(self, exc_type, exc_value, traceback):
        self.camera.release()

if __name__ == "__main__":
    lazy_feed = LazyVideoStream()
    lazy_feed.start()
    window = "window"
    cv2.namedWindow(window)
    
    while True:
        lazy_feed.request_queue.put(True)
        frame, codes = lazy_feed.frame_queue.get()
        lazy_feed.frame_queue.task_done()
        cv2.imshow(window, frame)
        cv2.waitKey(1)
        if codes:
            parallel_print(codes)
    