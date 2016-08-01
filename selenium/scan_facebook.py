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

    _driver.execute_script("""
var element = document.querySelector("#pagelet_growth_expanding_cta");
if (element)
    element.parentNode.removeChild(element);
""")

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
    screenshots_path = setup_selenium_screenshots_directory()

    # anonymous visit to facebook
    facebook_driver = authenticate_driver(setup_driver())

    # implicit wait
    facebook_driver = setup_implicit_wait(facebook_driver)

    # profile = webdriver.FirefoxProfile()
    # profile = webdriver.FirefoxProfile()
    # profile.set_preference('general.useragent.override', ua.random)
    #
    # driver = webdriver.Firefox(profile)
    # #
    # driver.implicitly_wait(10)

    #if not os.path.exists("FacebookCookies.pkl"):

    # driver.get("https://www.facebook.com")
    # assert "Facebook" in driver.title
    #_usr="jaziel.lopez@wolterskluwer.com", _pwd="wolterskluwer"

    # elem = driver.find_element_by_id("email")
    # elem.send_keys("jaziel.lopez@wolterskluwer.com")
    #
    # elem = driver.find_element_by_id("pass")
    # elem.send_keys("wolterskluwer")

    # Facebook does not include another submit button
    # elem = driver.find_element_by_css_selector('input[type="submit"]')
    # elem.click()

        # driver.save_screenshot('after-login.png')

    # pickle.dump(driver.get_cookies(), open("FacebookCookies.pkl", "wb"))


    ## attach
    # driver.get("https://www.facebook.com")

    # for cookie in pickle.load(open("FacebookCookies.pkl", "rb")):
    #     driver.add_cookie(cookie)

    request = requests.get('http://stage.obpplatform.com/plugin/ioc/rest.php?router=facebook.sites')

    json_response = request.json()

    urls = json_response['message']

    for url in urls:

        # go to the google home page
        # facebook_driver.get(url['url'])

        # visit a facebook page
        view_facebook_page(facebook_driver, url['id'], url['url'])

        time.sleep(2)

        # publish(api, visit)

    # user is logged in facebook
    # facebook_driver = authenticate_driver(setup_driver(), "juan.jaziel@gmail.com", "password")

except StandardError as _error:
    print _error.message


#
# elem = driver.find_element_by_css_selector(".input.textInput")
# elem.send_keys("Posted using Python's Selenium WebDriver bindings!")
# elem = driver.find_element_by_css_selector("input[value=\"Publicar\"]")
# elem.click()
#

# we have to wait for the page to refresh
# WebDriverWait(driver, 5)
#
# driver.save_screenshot('landing.png')
#
# driver.get("https://www.facebook.com/AmericanExpressUS")
#
# # we have to wait for the page to refresh
# WebDriverWait(driver, 5)
#

#
# driver.save_screenshot('AmericanExpressUS.png')

# driver.get("https://www.facebook.com/PowerBar")
#
# # we have to wait for the page to refresh
# WebDriverWait(driver, 5)
#
# driver.execute_script("""
# var element = document.querySelector("#pagelet_growth_expanding_cta");
# if (element)
#     element.parentNode.removeChild(element);
# """)
#
#
# driver.save_screenshot('PowerBar.png')

# driver.close()
