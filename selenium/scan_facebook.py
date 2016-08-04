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
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent
# from collector import publish
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def setup_driver(_user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:45.0) Gecko/20100101 Firefox/45.0"):

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


def authenticate_driver(_driver, _usr="jaziel.lopez@wolterskluwer.com", _pwd="wolterskluwer"):
    """
        Selenium Facebook Login
        :param _driver
        :param _usr:
        :param _pwd:
    """

    _driver.get("https://www.facebook.com")
    # assert "Facebook" in driver.title

    elem = _driver.find_element_by_id("email")
    elem.send_keys(_usr)

    elem = _driver.find_element_by_id("pass")
    elem.send_keys(_pwd)

    # Facebook does not include another submit button
    elem = _driver.find_element_by_css_selector('input[type="submit"]')
    elem.click()

    return _driver


def setup_selenium_screenshots_directory(dir_name="selenium_screenshots"):

    """
        Setup directory for site screenshots
        If parameter is passed in the directory will be created relative to where the python script is executed
        :param dir_name
    """

    # relative to the location where the script has been executed
    dir_target_screenshots = dir_name

    path_target_screenshots = os.path.join(os.getcwd(), dir_target_screenshots)

    if not os.path.isdir(path_target_screenshots):
        os.makedirs(path_target_screenshots, 0777)

    return path_target_screenshots


def view_facebook_page(_driver, _pageId=0, _page=""):

    """
        Visit a facebook page, capture raw content and take screenshot
        Allow any number of redirects until the page is loaded
        :param _driver
        :param _pageId
        :param _page
    """

    # if not _page:
    #     raise StandardError("Expected Facebook Page: None passed")
    #
    # if not _screenshots_path:
    #     raise StandardError("Expected screenshot directory path: None passed")

    # get content
    _driver.get(_page)

    WebDriverWait(_driver, 10)

    # _driver.save_screenshot(_page.replace('/', '//').lower() + '.png')

    # parse content
    _raw = _driver.find_element_by_xpath("/html/body").text

    # publish page raw result
    payload = {
        'router': 'save.facebook.site',
        'url_id': _pageId,
        'redirects_to': _driver.current_url,
        'raw': _raw

    }

    response = requests.post('http://stage.obpplatform.com/plugin/ioc/rest.php', data=payload)
    data = response.json()

    print data

try:

    ua = UserAgent()

    request = requests.get('http://stage.obpplatform.com/plugin/ioc/rest.php?router=facebook.sites')

    json_response = request.json()

    urls = json_response['message']

    # if len(sys.argv) == 1:
    #     raise StandardError("Expected facebook url and api host url to send results: None Received")
    #
    # if len(sys.argv) == 2:
    #     raise StandardError("Expected API url to send page visit results: None Received")
    #
    # visit_page = sys.argv[1]
    #
    # api = sys.argv[2]

    # setup selenium screenshots directory
    # screenshots_path = setup_selenium_screenshots_directory()
    #
    # # anonymous visit to facebook
    # facebook_driver = authenticate_driver(setup_driver())
    #
    # # implicit wait
    # facebook_driver = setup_implicit_wait(facebook_driver)

    # profile = webdriver.FirefoxProfile()
    # profile.set_preference('general.useragent.override', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:47.0) Gecko/20100101 Firefox/47.0")
    driver = webdriver.Firefox()

    driver.get("https://www.facebook.com")
    WebDriverWait(driver, 10)

    # driver.save_screenshot("before-login.png")

    elem = driver.find_element_by_id("email")
    elem.send_keys("jaziel.lopez@wolterskluwer.com")

    elem = driver.find_element_by_id("pass")
    elem.send_keys("wolterskluwer")

    elem = driver.find_element_by_css_selector('input[type="submit"]')
    elem.click()

    WebDriverWait(driver, 10)

    # driver.save_screenshot("post-login.png")

    for url in urls:

        syslog.syslog(syslog.LOG_INFO, 'Changing browser URL to {}'.format(url['url']))

        error_number = 0

        try:

            # get content
            driver.get(url['url'])

            WebDriverWait(driver, 10)

            # driver.save_screenshot(str(url['id'] + ".png"))

            # parse content
            _raw = driver.find_element_by_xpath("/html/body").text

            if len(_raw) > 0:

                # publish page raw result
                payload = {
                    'router': 'save.facebook.site',
                    'url_id': url['id'],
                    'redirects_to': driver.current_url,
                    'raw': _raw

                }

                response = requests.post('http://stage.obpplatform.com/plugin/ioc/rest.php', data=payload)
                data = response.json()

                syslog.syslog(syslog.LOG_INFO, 'URL {} has been saved '.format(url['url']))

                # time.sleep(10)
                # syslog.syslog(syslog.LOG_INFO, 'Sleep time is over and will continue up to the next url')
            else:

                raise TimeoutException('Page {} has not content: '.format(url['url']))

        except TimeoutException as exception:

            error_number += 1

            driver.save_screenshot('error' + str(error_number) + '.png')

            syslog.syslog(syslog.LOG_ERR, exception.message)

            print exception.message

        finally:

            syslog.syslog(syslog.LOG_INFO, 'Thread set to sleep 10 seconds')
            time.sleep(10)
            syslog.syslog(syslog.LOG_INFO, 'Sleep time is over and will continue up to the next url')

except StandardError as _error:
    print _error.message
