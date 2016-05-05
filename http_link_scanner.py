# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import sys
import json
import urllib
import httplib
import argparse
from scrapy.crawler import CrawlerProcess
from spider.Main import Links
sys.tracebacklimit = 0

try:

    # host to post and connect
    _host = "localhost"
    _port = 8030

    _headers = {"Accept": "text/plain"}
    _params = urllib.urlencode(
        {'router': 'domains'}
    )

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
    _process = CrawlerProcess()

    # feed process with domains
    # start crawler
    Links.start_urls = _domains
    _process.crawl(Links)
    _process.start()

except IOError:
    raise
except:
    raise
