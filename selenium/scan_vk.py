# Jaziel Lopez <juan.jaziel@gmail.com>
# Software Developer
# http://jlopez.mx

import os
import time
import sys
import pickle
from datetime import date
from urlparse import urlparse
from urlparse import urljoin
import requests
from selenium import webdriver
from fake_useragent import UserAgent
# from collector import publish
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0


def setup_driver(_user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:47.0) Gecko/20100101 Firefox/47.0"):

    profile = webdriver.FirefoxProfile('firefox.default')
    profile.set_preference('general.useragent.override', _user_agent)

    return webdriver.Firefox(profile)


def setup_implicit_wait(_driver, _time=10):
    """
        Setup driver timeout
        Implicit Wait - It instructs the web driver to wait for some time by poll the DOM.
        Once you declared implicit wait it will be available for the entire life of web driver instance.
        By default the value will be 0. If you set a longer default,
        then the behavior will poll the DOM on a periodic basis depending on the browser/driver implementation.
    :param _driver:
    :param _time
    :return:
    """

    _driver.implicitly_wait(_time)

    return _driver


def view_vk_page(_driver, _pageId=0, _page=""):

    """
        Visit a facebook page, capture raw content and take screenshot
        Allow any number of redirects until the page is loaded
        :param _driver
        :param _pageId
        :param _page
    """

    # get content
    _driver.get(_page)

    WebDriverWait(_driver, 5)

    # parse content
    _raw = _driver.find_element_by_xpath("/html/body").text

    # publish page raw result
    payload = {
        'router': 'save.vk.site',
        'url_id': _pageId,
        'redirects_to': _driver.current_url,
        'raw': _raw

    }

    response = requests.post('http://stage.obpplatform.com/plugin/ioc/rest.php', data=payload)
    data = response.json()

    print data

try:

    ua = UserAgent()

    vk_driver = setup_driver()

    # implicit wait
    vk_driver = setup_implicit_wait(vk_driver)

    request = requests.get('http://stage.obpplatform.com/plugin/ioc/rest.php?router=vk.sites')

    json_response = request.json()

    urls = json_response['message']

    for url in urls:

        view_vk_page(vk_driver, url['id'], url['url'])

        time.sleep(2)


except StandardError as _error:
    print _error.message
