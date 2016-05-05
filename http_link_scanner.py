# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import sys
import argparse
import json
import urllib
import httplib
from scrapy.crawler import CrawlerProcess
from spider.Main import Links, Images, Content
sys.tracebacklimit = 0

try:

    # host to post and connect
    _host = ""        # "localhost"
    _port = 0         # 8030

    _headers = {"Accept": "text/plain"}
    _conn = httplib.HTTPConnection(_host, _port)
    _conn.request('GET', '/plugin/ioc/rest.php?router=domains', '', _headers)
    _response = _conn.getresponse()

    if _response.status != 200:
        raise Exception("Unable to connect: " + _host + ":" + str(_port) + "\nReason: " + _response.reason + "\n" + _response.read())
        pass

    _domains = []
    _data = json.loads(_response.read())['message']

    for _domain in _data:
        print _domain['url']
        _domains.append(str(_domain['url']))

    _conn.close()

    # generate cache identifier
    _conn = httplib.HTTPConnection(_host, _port)
    _headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    _conn.request('POST', '/plugin/ioc/rest.php', urllib.urlencode({'router': 'cache'}), _headers)
    _response = _conn.getresponse()
    if _response.status != 200:
        raise Exception("Unable to connect: " + _host + ":" + str(_port) + "\nReason: " + _response.reason + "\n" + _response.read())
        pass

    _cache = json.loads(_response.read())['message']

    # _parser = argparse.ArgumentParser()
    # _parser.add_argument('--domains', help='List of domains JSON format')
    # _args = _parser.parse_args()
    # _file = _args.domains

    # _domains = []
    # with open(_file) as _file_domains:
    #     _data = json.load(_file_domains)
    #     for _domain in _data:
    #         print _domain['name']
    #         _domains.append(str(_domain['name']))

    # crawl process handler
    _process_links = CrawlerProcess()
    _process_images = CrawlerProcess()
    _process_raw = CrawlerProcess()

    # feed process with domains
    # start crawler
    Links.start_urls = _domains
    Links.port = _port
    Links.host = _host
    Links.cache = _cache

    Images.start_urls = _domains
    Images.port = _port
    Images.host = _host
    Images.cache = _cache

    Content.start_urls = _domains
    Content.port = _port
    Content.host = _host
    Content.cache = _cache

    _process_links.crawl(Links)
    _process_links.start()

    _process_images.crawl(Images)
    _process_images.start()

    _process_raw.crawl(Content)
    _process_raw.start()

except:
    raise
