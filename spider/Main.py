# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import sys
import scrapy
import httplib, urllib
import urlparse
from w3lib.html import remove_tags
from w3lib.html import remove_tags_with_content
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor


class Links(scrapy.Spider):
    name = 'links'

    # TODO: add try/catch block
    def parse(self, response):
        try:

            # collect links
            _extractor = LinkExtractor()
            _links = _extractor.extract_links(response)

            # link
            for _link in _links:

                try:
                    _headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                    _params = urllib.urlencode(
                        {'href': _link.url,  'content': _link.text, 'url': response.url, 'router': 'link'}
                    )

                    _conn = httplib.HTTPConnection("localhost", 8030)
                    _conn.request('POST', '/plugin/ioc/rest.php', _params, _headers)
                    _response = _conn.getresponse()

                    print _response.status, _response.reason
                    _data = _response.read()
                    print _data
                except Exception:
                    raise
            # pass
            #
            # _links = Selector(response)
            # _links.xpath('//link')
            #
            #
            # # save original
            # # filename = response.url.split("/")[-2] + '.html'
            # # with open(filename, 'wb') as f:
            # #     f.write(response.body)
            #
            # # parse and clean
            # _selector = Selector(response)
            # _html = remove_tags(remove_tags_with_content(_selector.xpath('//body')[0].extract(), which_ones=('script', 'style')))
            # _html = u''.join(_html).strip()
            #
            # # print and write cleaned content to a file
            #
            # with open('test.html', 'wb') as f:
            #     f.write(_html.encode('utf8'))
        except TypeError:
            print "Type error", sys.exc_info()
            raise


