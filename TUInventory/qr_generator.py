"""Handles QR-Code generation"""

import qrcode
import qrcode.image.svg as svg

def generate_qr(device):
    """Generate the QR-Code for a given device and store it locally as svg"""
    qr = qrcode.QRCode(version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=20,
        border=6)
    code = f"{device.uid} {device.article.name}"
    qr.add_data(code)
    qr.make(fit=True) # autosize according to data
    img = qr.make_image(image_factory=svg.SvgPathFillImage)
    img.save(f"{device.uid}_{device.article.name}.svg")

if __name__=="__main__":
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
    generate_qr(device)