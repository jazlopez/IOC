# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx
import scrapy
import httplib, urllib
from urlparse import urljoin
from w3lib.html import remove_tags
from w3lib.html import remove_tags_with_content
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy import Request


class Content(scrapy.Spider):
    name = 'content'
    cache = None
    start_urls = None
    host = None
    port = None

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]})


    def parse(self, response):

        try:
            # save original
            # # filename = response.url.split("/")[-2] + '.html'
            # # with open(filename, 'wb') as f:
            # #     f.write(response.body)
            #=
            # # print and write cleaned content to a file
            #
            # with open('test.html', 'wb') as f:
            #     f.write(_html.encode('utf8'))
            # parse and clean
            _selector = Selector(response)
            _html = remove_tags(remove_tags_with_content(_selector.xpath('//body')[0].extract(), which_ones=('script', 'style')))
            _html = u''.join(_html).strip()

            _html = _html.encode('utf8')
            _headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            _params = urllib.urlencode(
                {
                    'raw': _html,
                    'url': response.url,
                    'router': 'raw',
                    'cache': self.cache
                }
            )

            _conn = httplib.HTTPConnection(self.host, self.port)
            _conn.request('POST', '/plugin/ioc/rest.php', _params, _headers)
            _response = _conn.getresponse()

            print _response.status, _response.reason, _response.read()
            _data = _response.read()
            print _data
        except:
            raise


# parse and save images
class Images(scrapy.Spider):
    name = 'images'
    cache = None
    start_urls = None
    host = None
    port = None

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]})

    def parse(self, response):

        try:
            # collect images
            _select = Selector(response)
            _images = _select.xpath('//img/@src').extract()

            # link
            for _image in _images:
                print _image
                _headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                _params = urllib.urlencode(
                    {'src': urljoin(response.url, _image),
                     'url': response.url,
                     'router': 'image',
                     'cache': self.cache
                     }
                )

                _conn = httplib.HTTPConnection(self.host, self.port)
                _conn.request('POST', '/plugin/ioc/rest.php', _params, _headers)
                _response = _conn.getresponse()

                print _response.status, _response.reason
                _data = _response.read()
                print _data

        except:
            raise


# parse and save links
class Links(scrapy.Spider):
    name = 'links'
    cache = None
    start_urls = None
    host = None
    port = None

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, meta={'dont_redirect': True, 'handle_httpstatus_list': [301, 302]})

    def parse(self, response):

        try:
            # collect links
            _extractor = LinkExtractor()
            _links = _extractor.extract_links(response)

            # link
            for _link in _links:

                # do not post links which content is empty
                if _link.text:
                    _headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                    _params = urllib.urlencode(
                        {'href': _link.url,
                         'content': _link.text,
                         'url': response.url,
                         'router': 'link',
                         'cache': self.cache
                         }
                    )

                    _conn = httplib.HTTPConnection(self.host, self.port)
                    _conn.request('POST', '/plugin/ioc/rest.php', _params, _headers)
                    _response = _conn.getresponse()

                    print _response.status, _response.reason
                    _data = _response.read()
                    print _data
        except:
            raise


