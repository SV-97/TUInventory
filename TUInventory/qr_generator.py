"""Handles QR-Code generation"""

from logger import logger
import re

import qrcode
import qrcode.image.svg as svg

def generate_qr(device, path):
    """Generate the QR-Code for a given device and store it locally as svg"""
    qr = qrcode.QRCode(
        version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=20,
        border=6)
    code = f"id={device.uid} name={device.article.name}"
    qr.add_data(code)
    qr.make(fit=True) # autosize according to data
    
    filetype = re.match(r".*\.(?P<filetype>.*$)", str(path), re.IGNORECASE)\
        .group("filetype").lower() # could probably also use .suffix of Path object
    if filetype == "svg":
        img = qr.make_image(image_factory=svg.SvgPathFillImage)
    else:
        raise NotImplementedError("See qrcode-docs at https://pypi.org/project/qrcode/ to see how to install additional formats", filetype)
    img.save(str(path))
    logger.info(f"Succesfully created and saved qr-code for {device.uid}")


if __name__=="__main__":
    import pathlib
    class TestArticle():
        def __init__(self, name):
            self.name = name
    class TestDevice():
        def __init__(self, uid, code, article):
            self.uid = uid
            self.code = code
            self.article = article
    article = TestArticle("Article")
    device = TestDevice(10, "", article)
    generate_qr(device, pathlib.Path("test.svg"))