# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

from lxml import html
from urlparse import urljoin


class Normalizer:

    base = ''

    urls = []

    content = ''

    url = ''

    def __init__(self):
        pass

    def links(self):

        while True:
            tree = html.fromstring(self.content)
            _selector = tree.xpath("//a[not(starts-with(@href, 'http')) "
                                   "and not(starts-with(@href, 'mailto')) "
                                   "and not(starts-with(@href, 'skype')) "
                                   "and not(starts-with(@href, 'javascript'))]/@href")

            if len(_selector) == 0:
                break

            print ('Collected ' + str(len(_selector)) + ' links')

            for _link in _selector:
                print _link
                self.content = self.content.replace(_link, urljoin(self.base, _link))
                break

    def images(self):

        while True:
            tree = html.fromstring(self.content)
            _selector = tree.xpath("//img[not(starts-with(@src, 'http'))]/@src")

            if len(_selector) == 0:
                break

            print ('Collected ' + str(len(_selector)) + ' image')

            for _link in _selector:
                print _link
                self.content = self.content.replace(_link, urljoin(self.base, _link))
                break

    def styles(self):

        while True:
            tree = html.fromstring(self.content)
            _selector = tree.xpath("//link[not(starts-with(@href, 'http'))]/@href")

            if len(_selector) == 0:
                break

            print ('Collected ' + str(len(_selector)) + ' style')

            for _link in _selector:
                print _link
                self.content = self.content.replace(_link, urljoin(self.base, _link))
                break