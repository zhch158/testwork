# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import warnings

from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.base import keyword, LibraryComponent
from SeleniumLibrary.keywords import BrowserManagementKeywords

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.remote.mobile import Mobile
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.firefox.remote_connection import FirefoxRemoteConnection
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver

from robot.api import logger
from SeleniumLibrary.utils import timestr_to_secs

import urllib.parse as urllib
import os
import shutil
import time
import json
import types

# This webdriver can directly attach to an existing session.
class AttachableWebDriver(WebDriver):
    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub',
                 desired_capabilities=None, browser_profile=None, proxy=None,
                 keep_alive=False, file_detector=None, session_id=None, w3c=True):
        """
        Create a new driver that will issue commands using the wire protocol.

        :Args:
         - command_executor - Either a string representing URL of the remote server or a custom
             remote_connection.RemoteConnection object. Defaults to 'http://127.0.0.1:4444/wd/hub'.
         - desired_capabilities - A dictionary of capabilities to request when
             starting the browser session. Required parameter.
         - browser_profile - A selenium.webdriver.firefox.firefox_profile.FirefoxProfile object.
             Only used if Firefox is requested. Optional.
         - proxy - A selenium.webdriver.common.proxy.Proxy object. The browser session will
             be started with given proxy settings, if possible. Optional.
         - keep_alive - Whether to configure remote_connection.RemoteConnection to use
             HTTP keep-alive. Defaults to False.
         - file_detector - Pass custom file detector object during instantiation. If None,
             then default LocalFileDetector() will be used.
        """
        if desired_capabilities is None:
            raise WebDriverException("Desired Capabilities can't be None")
        if not isinstance(desired_capabilities, dict):
            raise WebDriverException("Desired Capabilities must be a dictionary")
        if proxy is not None:
            warnings.warn("Please use FirefoxOptions to set proxy",
                          DeprecationWarning)
            proxy.add_to_capabilities(desired_capabilities)
        if(desired_capabilities["browserName"]=='firefox'):
            command_executor = FirefoxRemoteConnection(remote_server_addr=command_executor)
        self.command_executor = command_executor
        if type(self.command_executor) is bytes or isinstance(self.command_executor, str):
            self.command_executor = RemoteConnection(command_executor, keep_alive=keep_alive)

        self._is_remote = True
        self.session_id = session_id  # added
        self.capabilities = dict(desired_capabilities)
        self.error_handler = ErrorHandler()
        self.start_client()
        if browser_profile is not None:
            warnings.warn("Please use FirefoxOptions to set browser profile",
                          DeprecationWarning)

        if session_id:
            if desired_capabilities["browserName"]!="firefox":
                self.connect_to_session(desired_capabilities)  # added
            else:
                pass
            self.w3c = w3c  # modified by zhengchun
        else:
            self.start_session(desired_capabilities, browser_profile)

        self._switch_to = SwitchTo(self)
        self._mobile = Mobile(self)
        self.file_detector = file_detector or LocalFileDetector()

    def connect_to_session(self, desired_capabilities):
        self.command_executor._commands['GET_SESSION'] = ('GET', '/session/$sessionId')  # added

        response = self.execute('GET_SESSION', {
            'desiredCapabilities': desired_capabilities,
            'sessionId': self.session_id,
        })
        # self.session_id = response['sessionId']
        self.capabilities = response['value']

class BrowserKeywords(BrowserManagementKeywords):

    # def __init__(self, timeout=5.0, implicit_wait=0.0,
    #              run_on_failure='Capture Page Screenshot',
    #              screenshot_root_directory=None):
    #     super().__init__(timeout, implicit_wait, run_on_failure, screenshot_root_directory)

    def _dump_dic(self, target, dic_list):
        f=open(target,"w", encoding="utf-8")
        for dic in dic_list:  
            json.dump(dic, f, ensure_ascii=False)
            f.write("\n")
        f.close()

    def _load_dic(self, src, dic_list):
        f=open(src,"r", encoding="utf-8")
        # data=list()
        for line in f:
            l=line.strip()
            if(len(l)==0 or l[0]=="#"):
                continue
            else:
                dic_list.append(json.loads(l))
        # logger.debug(dic_list)
        f.close()

    def _save_browser_params(self, browser, webfile):
        params = {}
        params["session_id"] = browser.session_id
        params["server_url"] = browser.command_executor._url
        params["w3c"] = browser.w3c
        params["capabilities"] = browser.capabilities
        dic_list=list()
        dic_list.append(params)
        self._dump_dic(webfile, dic_list)

    @keyword
    def my_connect_browser(self, paramsfile='params.json', alias=None):
        """connect a exist browser instance.

        The ``browser`` argument specifies which browser to use, and the
        supported browser are listed in the table below. The browser names
        are case-insensitive and some browsers have multiple supported names.

        |    = Browser =    |        = Name(s) =       |
        | Firefox           | firefox, ff              |
        | Google Chrome     | googlechrome, chrome, gc |

        To be able to actually use one of these browsers, you need to have
        a matching Selenium browser driver available. See the
        [https://github.com/robotframework/SeleniumLibrary#browser-drivers|
        project documentation] for more details. Headless Firefox and
        Headless Chrome are new additions in SeleniumLibrary 3.1.0
        and require Selenium 3.8.0 or newer.

        Optional ``alias`` is an alias given for this browser instance and
        it can be used for switching between browsers. An alternative
        approach for switching is using an index returned by this keyword.
        These indices start from 1, are incremented when new browsers are
        opened, and reset back to 1 when `Close All Browsers` is called.
        See `Switch Browser` for more information and examples.

        Examples:
        | `My Connect Browser` | Chrome  | params.json | alias=Chrome |
        | `My Connect Browser` | FireFox  | params.json | alias=ff |

        """
        dic_list=list()
        self._load_dic(paramsfile, dic_list)
        params=dic_list[0]
        logger.info("params:[%s]" %(params))
        driver = AttachableWebDriver(command_executor=params["server_url"],
                    desired_capabilities=params["capabilities"],
                    session_id=params["session_id"], w3c=params["w3c"])
        driver.set_script_timeout(self.ctx.timeout)
        driver.implicitly_wait(self.ctx.implicit_wait)
        if self.ctx.speed:
            self._monkey_patch_speed(driver)
        self.debug('Connect to exist browser with session id %s.' % driver.session_id)
        return self.ctx.register_driver(driver, alias)

    def _start_chrome(self, remote_url, downloaddir):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {'download.default_directory':downloaddir}
        chromeOptions.add_experimental_option('prefs',prefs)
        cap=chromeOptions.to_capabilities()
        browser = AttachableWebDriver(command_executor=remote_url,
            desired_capabilities=cap)
        return browser

    def _start_firefox(self, remote_url, downloaddir, firefox_profile):
        profile = webdriver.FirefoxProfile(firefox_profile)
        profile.set_preference('browser.download.dir',downloaddir)
        profile.set_preference('browser.download.folderList',2)
        profile.set_preference('browser.download.manager.showWhenStarting',False)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk','application/octet-stream ,application/zip,application/kswps,application/pdf')

        firefoxOptions = webdriver.FirefoxOptions()
        cap=firefoxOptions.to_capabilities()
        browser = AttachableWebDriver(command_executor=remote_url,
                desired_capabilities=cap,
                browser_profile=profile)  
        return browser

    @keyword
    def my_open_browser(self, url, browser='firefox', alias=None,
                     remote_url='http://127.0.0.1:4444', downloaddir='X:/TEMP',
                     ff_profile_dir='F:/workspace/selenium-profile', paramsfile='params.json'):
        """Opens a new browser instance to the given ``url``.

        The ``browser`` argument specifies which browser to use, and the
        supported browser are listed in the table below. The browser names
        are case-insensitive and some browsers have multiple supported names.

        |    = Browser =    |        = Name(s) =       |
        | Firefox           | firefox, ff              |
        | Google Chrome     | googlechrome, chrome, gc |
        To be able to actually use one of these browsers, you need to have
        a matching Selenium browser driver available. See the
        [https://github.com/robotframework/SeleniumLibrary#browser-drivers|
        project documentation] for more details. Headless Firefox and
        Headless Chrome are new additions in SeleniumLibrary 3.1.0
        and require Selenium 3.8.0 or newer.

        Optional ``alias`` is an alias given for this browser instance and
        it can be used for switching between browsers. An alternative
        approach for switching is using an index returned by this keyword.
        These indices start from 1, are incremented when new browsers are
        opened, and reset back to 1 when `Close All Browsers` is called.
        See `Switch Browser` for more information and examples.

        Optional ``remote_url`` is the URL for a
        [https://github.com/SeleniumHQ/selenium/wiki/Grid2|Selenium Grid].

        Optional ``desired_capabilities`` can be used to configure, for example,
        logging preferences for a browser or a browser and operating system
        when using [http://saucelabs.com|Sauce Labs]. Desired capabilities can
        be given either as a Python dictionary or as a string in format
        ``key1:value1,key2:value2``.
        [https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities|
        Selenium documentation] lists possible capabilities that can be
        enabled.

        Optional ``ff_profile_dir`` is the path to the Firefox profile
        directory if you wish to overwrite the default profile Selenium
        uses. Notice that prior to SeleniumLibrary 3.0, the library
        contained its own profile that was used by default.

        Examples:
        | `My Open Browser` | http://example.com | Chrome  | remote_url=http://127.0.0.1:9515 | downloaddir=X:${/}TEMP | paramsfile=params.json
        | `My Open Browser` | http://example.com | Firefox | remote_url=http://127.0.0.1:4444 | alias=Firefox |

        If the provided configuration options are not enough, it is possible
        to use `Create Webdriver` to customize browser initialization even
        more.

        Applying ``desired_capabilities`` argument also for local browser is
        new in SeleniumLibrary 3.1.
        """
        logger.info("browser[%s], url[%s], alias[%s], remote_url[%s], downloaddir[%s], ff_profile[%s], paramsfile[%s]" %(browser, url, alias, remote_url, downloaddir, ff_profile_dir, paramsfile))
        if(browser.lower()=='firefox'):
            driver=self._start_firefox(remote_url, downloaddir, ff_profile_dir)
        elif(browser.lower()=='chrome'):
            driver=self._start_chrome(remote_url, downloaddir)
        else:
            raise NameError("browser name[%s] is not in [chrome, firefox]" % (browser))

        logger.info("ctx.timeout[%s], ctx.implicit_wait[%s]" %(self.ctx.timeout, self.ctx.implicit_wait))
        driver.set_script_timeout(timestr_to_secs(self.ctx.timeout))
        driver.implicitly_wait(timestr_to_secs(self.ctx.implicit_wait))
        if self.ctx.speed:
            self._monkey_patch_speed(driver)

        try:
            driver.get(url)
        except Exception:
            self.ctx.register_driver(driver, alias)
            self.debug("Opened browser with session id %s but failed "
                       "to open url '%s'." % (driver.session_id, url))
            raise
        self.debug('Opened browser with session id %s.' % driver.session_id)
        self._save_browser_params(driver, paramsfile)
        return self.ctx.register_driver(driver, alias)

class InheritSeleniumLibrary(SeleniumLibrary):

    def _delete_file(self, filename):
        if(os.access(filename, os.R_OK)):
            os.remove(filename)

    def _change_file_name(self, src, target):
        i=0
        p_f_l=-1
        while(i<20):
            if(os.access(src, os.R_OK)):
                statinfo=os.stat(src)
                f_l=statinfo.st_size
                #文件至少有1个字节
                if(p_f_l==f_l and f_l>1):
                    break
                else:
                    p_f_l=f_l
                    time.sleep(3)
            else:
                time.sleep(3)
            i+=1
        if(i==20):
            raise AssertionError("Original file[%s] is used or not exist" %(src))
        else:
            try:
                head, tail = os.path.split(target)
                if head and tail and not os.path.exists(head):
                    os.makedirs(head)
                shutil.move(src, target)
            except OSError as e:
                raise AssertionError("rename file <%s> --> <%s> error except[%s]" %(src, target, e))
            else:
                pass

    @keyword
    def title_should_start_with(self, expected):
        """the title of current page should start with 'expected'
        """
        title = self.get_title()
        if not title.startswith(expected):
            raise AssertionError("Title '%s' did not start with '%s'" % (title, expected))

    @keyword
    def switch_frame(self, frame):
        """goto iframe with name include 'frame'
        """
        self.element = self.get_webelements("tag:iframe")
        frame_name = ""
        for el in self.element:
            frame_name = el.get_attribute("name")
            if(frame in frame_name):
                break
            else:
                frame_name = ""
        if(frame_name == ""):
            raise NameError("iframe name '%s' did not in '%s'" % (frame, str(self.element)))
        else:
            self.select_frame(frame_name)
    
    @keyword
    def get_browser_desired_capabilities(self):
        logger.info('Getting currently open browser desired capabilities')
        return self.driver.desired_capabilities

    @keyword
    def get_report_filename(self, locator, downloaddir, YM, SAVEDIR):
        """根据'locator'的'value', downloaddir, YM, SAVEDIR组成原文件名，目标文件名
        """
        orig_file = self.get_value(locator)

        f_dir = downloaddir.strip()

        y_m = YM.strip().replace("-", "")
        t_dir_orig = SAVEDIR.strip()
        t_dir = t_dir_orig.replace("-", "")

        target_file = urllib.unquote(orig_file)
        if(self.get_browser_desired_capabilities()["browserName"].lower()=='firefox'):
            orig_file = f_dir + "/" + orig_file + ".xls"
        else:
            orig_file = f_dir + "/" + target_file + ".xls"   #chrome会自动转码
        target_file = t_dir + "/" + target_file.strip() + "-" + y_m + ".xls"

        return orig_file, target_file

    @keyword
    def delete_report_file(self, orig_file, target_file):
        """如果文件存在，删除原文件，目标文件
        """
        if(os.access(orig_file, os.R_OK)):
            self._delete_file(orig_file)

        if(os.access(target_file, os.R_OK)):
            self._delete_file(target_file)

        # if(ret_o or ret_t):
        #     raise AssertionError("delete_report_file[origal=%s(%d), target=%s(%d)] error " %(orig_file, ret_o, target_file, ret_t))

    @keyword
    def rename_file(self, orig_file, target_file):
        """判断原文件下载完成后，将原文件移动到目标文件
        """
        self._change_file_name(orig_file, target_file)

    @keyword
    def my_wait_until_element_presence(self, locator, seconds):
        loc_type, loc_tag=locator.split(":")
        logger.info("locator[%s], seconds[%s], loc_type[%s], loc_tag[%s]" %(locator, seconds, loc_type, loc_tag))
        timeout=int(seconds)
        times=0
        while(times<3):
            try:
                times += 1
                if(loc_type.upper() == "ID"):
                    self.element = WebDriverWait(self.driver, timeout, 1).until(EC.presence_of_element_located((By.ID, loc_tag)))
                elif(loc_type.upper() == "CSS"):
                    self.element = WebDriverWait(self.driver, timeout, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, loc_tag)))
                elif(loc_type.upper() == "NAME"):
                    self.element = WebDriverWait(self.driver, timeout, 1).until(EC.presence_of_element_located((By.NAME, loc_tag)))
                else:
                    raise AssertionError("my_wait[locator=%s, timeout=%s, loc_type=%s, loc_tag=%s] error " %(locator, seconds, loc_type.upper(), loc_tag))
                break
            except Exception as e:
                logger.error("times[%d], loc_type[%s], loc_tag[%s], Exception[%s]" %(times, loc_type, loc_tag, e))
                time.sleep(1)
        else:
            raise AssertionError("my_wait[locator=%s, timeout=%s, loc_type=%s, loc_tag=%s] error " %(locator, seconds, loc_type.upper(), loc_tag))

    @keyword
    def my_wait_until_element_visibility(self, locator, seconds):
        loc_type, loc_tag=locator.split(":")
        logger.info("locator[%s], seconds[%s], loc_type[%s], loc_tag[%s]" %(locator, seconds, loc_type, loc_tag))
        timeout=int(seconds)
        times=0
        while(times<3):
            try:
                times += 1
                if(loc_type.upper() == "ID"):
                    self.element = WebDriverWait(self.driver, timeout, 1).until(EC.visibility_of_element_located((By.ID, loc_tag)))
                elif(loc_type.upper() == "CSS"):
                    self.element = WebDriverWait(self.driver, timeout, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, loc_tag)))
                elif(loc_type.upper() == "NAME"):
                    self.element = WebDriverWait(self.driver, timeout, 1).until(EC.visibility_of_element_located((By.NAME, loc_tag)))
                else:
                    raise AssertionError("my_wait[locator=%s, timeout=%s, loc_type=%s, loc_tag=%s] error " %(locator, seconds, loc_type.upper(), loc_tag))
                break
            except Exception as e:
                logger.error("times[%d], loc_type[%s], loc_tag[%s], Exception[%s]" %(times, loc_type, loc_tag, e))
                time.sleep(1)
        else:
            raise AssertionError("my_wait[locator=%s, timeout=%s, loc_type=%s, loc_tag=%s] error " %(locator, seconds, loc_type.upper(), loc_tag))

class ExtendedSeleniumLibrary(InheritSeleniumLibrary):

    def __init__(self, timeout=5.0, implicit_wait=0.0,
                 run_on_failure='Capture Page Screenshot',
                 screenshot_root_directory=None):
        SeleniumLibrary.__init__(self, timeout=float(timeout), implicit_wait=float(implicit_wait),
                                 run_on_failure=run_on_failure,
                                 screenshot_root_directory=screenshot_root_directory)
        # self.add_library_components([BrowserKeywords(self), DesiredCapabilitiesKeywords(self)])

        self.add_library_components([BrowserKeywords(self)])
        # super().__init__(self, timeout=timeout, implicit_wait=implicit_wait,
        #                          run_on_failure=run_on_failure,
        #                          screenshot_root_directory=screenshot_root_directory)
