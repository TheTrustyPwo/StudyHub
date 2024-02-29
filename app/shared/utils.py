from urllib.parse import urlparse

from PIL import Image


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_image(content):
    try:
        image = Image.open(content)
        image.verify()
        return True
    except:
        return False
