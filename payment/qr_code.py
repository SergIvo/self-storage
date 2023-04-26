import os

import qrcode
from django.conf import settings
 

def make_qr(data, path):
    img = qrcode.make(data)
    image_path = os.path.join(settings.BASE_DIR, path)
    img.save(image_path)
