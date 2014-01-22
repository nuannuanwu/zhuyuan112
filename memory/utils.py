from userena.utils import generate_sha1

def upload_to_mugshot(instance, filename):
    """
    Uploads a mugshot for a user to the ``USERENA_MUGSHOT_PATH`` and saving it
    under unique hash for the image. This is for privacy reasons so others
    can't just browse through the mugshot directory.

    """
    extension = filename.split('.')[-1].lower()
    salt, hash = generate_sha1(instance.id)
    return '%(path)s/%(hash)s.%(extension)s' % {
            'path': instance.__class__.__name__.lower(),
            'hash': hash[:22],
            'extension': extension
            }
