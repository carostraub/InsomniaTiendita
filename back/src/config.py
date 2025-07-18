from urllib.parse import urlparse
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def obtener_public_id(url):
    """Extrae el public_id de una URL de Cloudinary"""
    if not url:
        return None
    path = urlparse(url).path
    return '/'.join(path.split('/')[-2:]).split('.')[0]