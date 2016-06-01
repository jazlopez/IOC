# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import os
import scrapy
import requests
from time import time
from Normalizer import Normalizer


class Site(scrapy.Spider):
    # name of crawler
    name = 'site'
    # urls to scrap from
    start_urls = []
    # host to respond with a file
    host = ''
    # host port
    port = ''

    # parse response
    def parse(self, response):
        try:
            _normalizer = Normalizer()
            _normalizer.base = response.url
            _normalizer.content = str(response.body)

            # begin
            # replacement
            _normalizer.links()
            _normalizer.styles()
            _normalizer.images()

            # write file to os
            filename = time().split('.')[0] +  response.url
            filename = filename.replace('http://', '')
            filename = filename.replace('https://', '')
            filename = filename.replace('www.', '')
            filename = filename.replace('/', '_')
            filename += '.html'

            if os.path.exists(filename):
                f = file(filename, "r+")
            else:
                f = file(filename, "w")

            f.write(_normalizer.content)

            # attempt to send file back to requester
            requests.post( self.host + self.port + '/plugin/ioc/rest', files={'file': (f.name, f)})

            f.close()
        except:
            # TODO: log to file: site timeout
            raise