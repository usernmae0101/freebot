import hashlib

from helpers import CONSTANTS


class Crypto:
    @staticmethod
    def create_fingerprint():
        md5 = hashlib.md5()
        md5.update(('###'.join([CONSTANTS.USER_AGENT,
                               'x'.join(['1024', '1280', '24']),
                               '-420',
                               'true',
                               'true',
                               '::'.join(['BookReader', '', 'application/epub+zip~epub,application/x-fictionbook+xml~fb2,application/x-zip-compressed-fb2~fb2.zip;Chromium PDF Plugin',
                                          'Portable Document Format', 'application/x-google-chrome-pdf~;Chromium PDF Viewer', '', 'application/pdf~pdf;Native Client',
                                          '', 'application/x-nacl~,application/x-pnacl~;Shockwave Flash', 'Shockwave Flash 32.0 r0::application/x-shockwave-flash~swf,application/futuresplash~spl'
                                         ])
                               ])).encode('utf-8'))
        
        return md5.hexdigest()

    @staticmethod
    def create_token(hash: str):
        return hashlib.sha256(hash.encode('utf-8')).hexdigest()

    @staticmethod
    def create_fingerprint2():
        return '3266881495' # he-he