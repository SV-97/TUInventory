import qrcode
import qrcode.image.svg

# https://pypi.org/project/qrcode/
def generate_qr(device):
    qr = qrcode.QRCode(version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_H, 
        box_size=20,
        border=6)
    qr.add_data(device.code)
    qr.make(fit=True) # autosize according to data

    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathFillImage)
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
    article = TestArticle("Der Schokopanzer")
    device = TestDevice(10, "This is our code", article)
    generate_qr(device)