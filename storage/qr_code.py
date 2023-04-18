import os

import qrcode
from django.conf import settings
 

def make_qr_png(data):
    img = qrcode.make(data)
    image_path = os.path.join(settings.BASE_DIR, 'qr_code.png')
    img.save(image_path)
