# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import os
import time
import syslog
import sys
import pickle
from datetime import date
from urlparse import urlparse
from urlparse import urljoin
import requests
import ipaddress
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException

MAX_PROXY_FAILED_ATTEMPTS = 3
PROXY_API_USER = 'ivan'
PROXY_API_PASSWORD = '123'


class FatalException(Exception):

    def __init__(self, message=''):
        self.message = message


def yield_proxy(previous_proxy=""):

    """
    :return Proxy
    """
    try:
        print "INFO: Requesting proxy, please wait ..."

        proxy_request = requests.get('http://hawkapi.citizenhawk.net/proxy.json?provider=syptec',
                                     auth=HTTPBasicAuth(PROXY_API_USER, PROXY_API_PASSWORD))
        syptec = proxy_request.json()
        eligible_proxy = syptec['proxy']['host'] # as string

        if previous_proxy:

            ip_eligible_proxy = ipaddress.ip_address(unicode(eligible_proxy))  # as ip address object for network lookup
            previous_network = ipaddress.ip_network(unicode(previous_proxy))  # network

            if ip_eligible_proxy in previous_network:
                print "INFO: Consecutive network proxies are not allowed. Requesting a new proxy..."
                yield_proxy(previous_proxy)

        return eligible_proxy

    except StandardError as yield_proxy_error:
        print yield_proxy_error

try:

    print "INFO: Requesting youtube sites from IOC rest"
    response = requests.get('http://stage.obpplatform.com/plugin/ioc/rest.php?router=youtube.sites')
    json_response = response.json()

    if 'error' in json_response.keys():
        raise Exception('Unable to fetch youtube sites from IOC rest')

    proxy_failed_attempts = 0
    syptec_proxy = ""

    for url in json_response['message']:

        try:

            # ff user agent
            ff_user_agent = UserAgent().firefox

            # each url to use a new profile for firefox
            # each profile use a different proxy ip address
            # prevent to have two profile within the same network one after other

            if proxy_failed_attempts == MAX_PROXY_FAILED_ATTEMPTS:
                raise FatalException(message='Exhausted proxy connection attempts.')

            syptec_proxy = yield_proxy(syptec_proxy)

            syptec_proxy_port = syptec_proxy + ":8888"  # port 8888 static for syptec

            driver_proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': syptec_proxy_port,
                'ftpProxy': '',
                'sslProxy': '',
                'noProxy': ''  # set this value as desired
            })

            ff_profile = webdriver.FirefoxProfile()
            ff_profile.set_preference('general.useragent.override', ff_user_agent)
            driver = webdriver.Firefox(firefox_profile=ff_profile, proxy=driver_proxy)

            # get contents
            driver.get(url['url'])

            print "Request to: {}".format(url['url'])

            WebDriverWait(driver, 10)

            if not len(driver.page_source):
                raise WebDriverException

            # parse content
            raw = driver.find_element_by_xpath("/html/body").text

            # publish page raw result
            payload = {
                'router': 'save.youtube.site',
                'url_id': url['id'],
                'redirects_to': driver.current_url,
                'raw': raw

            }

            response = requests.post('http://stage.obpplatform.com/plugin/ioc/rest.php', data=payload)

            data = response.json()

            print data

        except TimeoutException as _error:

            print "INFO: {} has time out. Process is moving forward to the next url.\nERROR: {}"\
                .format(url['url'], _error.message)

        except UnexpectedAlertPresentException as _error:

            print "INFO: {} has encountered an error and will move forward to the next url\nERROR: {}"\
                .format(url['url'], _error.message)

        except NoSuchElementException as _error:

            print "INFO: {} has not /html/body element " \
                  "and will move forward to the next url \nERROR:{} ".format(url['url'], _error.message)

        except WebDriverException as _error:

            print "ERROR: Proxy {} has refused connection\n" \
                  "INFO: Process will attempt to check proxy connections only {} times max. before exit"\
                .format(syptec_proxy, MAX_PROXY_FAILED_ATTEMPTS)

            proxy_failed_attempts += 1

        except FatalException as fatal:

            print fatal.message

            raise Exception

        finally:

            driver.quit()

            time.sleep(10)

except Exception as e:

    print "INFO: Premature end of script due to an unrecoverable error."

    if e.message:
        print "FATAL: {}".format(e.message)

finally:
    print "{}\n{}\n{}\n{}\n".format("=" * 35, "Author: Jaziel Lopez", "Contact: <juan.jaziel@gmail.com>", "=" * 35)
