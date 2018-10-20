# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import chardet
import urllib.parse as urllib
import os
import sys
import getopt
from time import sleep
import time
import copy
import logging

sys.path.extend([".", "../pylib"])
import logger
from webdriver import myFirefox
# from webdriver.myFirefox.support.ui import WebDriverWait
# from utility import load_dic, delete_file, change_file_name, sub_var_value, load_from_yaml, setup_logging, load_xls
from utility import load_dic, delete_file, change_file_name, load_xls, gen_report_name

from httprunner import exception, testcase, utils
from httprunner.runner import Runner

from HTMLTestRunner_zc import HTMLTestRunner, stdout_redirector, stderr_redirector

__RETCODE__ = "retcode"
__STEP__ = "step"
__RETMSG__ = "retmsg"

def do_login(browser):
    browser.get('http://it.yusys.com.cn/yusys/login.html')
    browser.find_element_by_id("loginname").send_keys("zhengchun")
    browser.find_element_by_id("password").send_keys("Zhch1234")
    browser.find_element_by_id("checkcode").clear()
    # enc=sys.getfilesystemencoding()
    prompt_str = "请在浏览器中输入验证码，返回命令窗口，按任意键继续..."
    input(prompt_str)
    browser.find_element_by_id("login_btn").click()
    return 0


def connect_browser(conf_dict):
    fox_profile=conf_dict["firefoxprofile"]
    webfile = conf_dict["session"]
    filedir = conf_dict["downloaddir"]
    logger.log_debug("webfile[%s] download[%s]" % (webfile, filedir))

    dic_list = list()
    load_dic(webfile, dic_list)
    params = dic_list[0]
    logger.log_debug("%s" %(params))
    browser = myFirefox.myWebDriver(capabilities=params["capabilities"], service_url=params["server_url"],
                                    session_id=params["session_id"])
    logger.log_debug("%s" %browser.capabilities)
    logger.log_debug("%s" %browser.command_executor._url)
    logger.log_debug("%s" %browser.session_id)
    return browser

class PageSimulation(Runner):

    @classmethod
    def setUpClass(cls):
        logger.log_info("Start class[%s]" %cls.__name__)

    def __init__(self, conf_dict, browser):
        super().__init__(conf_dict)
        self.browser=browser
        self.conf_dict=conf_dict
        self.SCREENSHOT_B_TAG = "<selenium_screenshot>"
        self.SCREENSHOT_E_TAG = "</selenium_screenshot>"
        self.step=0
        self.element=None
        self.act_list=list()
        self.retval=dict()
        self.retval[__RETCODE__]=0
        self.retval[__STEP__]=0
        self.retval[__RETMSG__]=""

    def _get_windows_img(self):
        browser=self.browser
        reportdir=self.conf_dict.get("reportdir", os.getcwd())
        browser.switch_to_default_content()
        # 定义date为日期，time为时间
        date = time.strftime("%Y%m%d")
        file_path = reportdir + "/" + date + "/screenshots/"
        fullpath = os.path.abspath(file_path)
        # 判断是否定义的路径目录存在，不能存在则创建
        if not os.path.exists(fullpath):
            os.makedirs(fullpath)

        rq = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        screen_name = fullpath + '/' + rq + '.png'
        screen_name = os.path.abspath(screen_name)
        print("%s%s%s" % (self.SCREENSHOT_B_TAG, screen_name, self.SCREENSHOT_E_TAG))
        try:
            browser.get_screenshot_as_file(screen_name)
            # logger.log_info("save screenshot to [%s]" %(screen_name))
        except NameError as e:
            logger.log_error("Failed to take screenshot! [%s]" % (screen_name), exc_info=True)
            return -1
        return 0


    # def get_filename(YM, SAVEDIR, browser, element, data_dic, vars, act_list, step=None):
    def get_filename(self, YM, SAVEDIR):
        # el = WebDriverWait(browser, 20, 0.5).until(
        #                     EC.presence_of_element_located((By.NAME, "saveAsName")))
        vars=self.conf_dict
        orig_file = self.element.get_attribute("value")

        f_dir = vars["downloaddir"].strip()

        y_m = YM.strip().replace("-", "")
        t_dir_orig = SAVEDIR.strip()
        t_dir = t_dir_orig.replace("-", "")

        # target_file=urllib.unquote(orig_file).encode("raw_unicode_escape")
        target_file = urllib.unquote(orig_file)
        target_file = t_dir + "/" + target_file.strip() + "-" + y_m + ".xls"
        orig_file = f_dir + "/" + orig_file + ".xls"

        retval = {}
        retval[__RETCODE__] = 0
        retval[0] = orig_file
        retval[1] = target_file
        return retval


    def switch_to_default_content(self):
        # browser.switch_to.parent_frame()
        # browser.refresh()
        sleep(3)
        self.browser.switch_to_default_content()
        return 0

    def goto(self, key, value, stepname):
        retval = {}
        retcode = 0
        act_list=self.act_list
        step=self.step
        i = 0
        if(key == value):
            step_len = len(act_list[step:])
            while i < step_len:
                i += 1
                action = act_list[step+1]
                if(action["STEPNAME"] == stepname):
                    retcode = 0
                    break
            if(i == step_len):
                logger.log_error("step[%s] not found in act_list[%s]" %
                            (stepname, act_list))
                retcode = -1

        retval[__RETCODE__] = retcode
        if(retcode != 0):
            retval[__STEP__] = 0
            retval[__RETMSG__] = "step['%s'] not found in act_list[%s]" % (
                stepname, act_list)
        else:
            retval[__STEP__] = i
            retval[__RETMSG__] = ""

        return retval


    def assert_file(self, target_file):
        # orig_file, target_file = get_filename(
        #     YM, SAVEDIR, browser, element, vars, data_dic)
        if(os.access(target_file, os.R_OK)):
            return 0
        else:
            return -1


    def del_file(self, orig_file, target_file):
        ret_o = 0
        ret_t = 0

        # orig_file, target_file = get_filename(
        #     YM, SAVEDIR, browser, element, vars, data_dic)
        if(os.access(orig_file, os.R_OK)):
            ret_o = delete_file(orig_file)

        if(os.access(target_file, os.R_OK)):
            ret_t = delete_file(target_file)

        # retval[__RETCODE__]= ret_o+ret_t
        # if(retval[__RETCODE__]!=0):
        #     retval[__RETMSG__]="del_file error " + orig_file + " " + target_file
        # retval[__STEP__]=0
        return ret_o+ret_t


    def rename_file(self, orig_file, target_file):
        # orig_file, target_file = get_filename(
        #     YM, SAVEDIR, browser, element, vars, data_dic)
        return change_file_name(orig_file, target_file)

    #首先解析类中的自定义函数
    def _eval_content_with_bindings(self, content):
        functions_list = testcase.extract_functions(content)
        testcase_parser=self.context.testcase_parser
        if(functions_list==[]):
            return testcase_parser.eval_content_with_bindings(content)

        for func_content in functions_list:
            function_meta = testcase.parse_function(func_content)
            func_name = function_meta['func_name']
            func=getattr(self, func_name, None)
            #类中没有相应的函数
            if(func==None):
                return testcase_parser.eval_content_with_bindings(content)

            args = function_meta.get('args', [])
            kwargs = function_meta.get('kwargs', {})
            args = self._eval_content_with_bindings(args)
            kwargs = self._eval_content_with_bindings(kwargs)

            eval_value = func(*args, **kwargs)

            func_content = "${" + func_content + "}"
            if func_content == content:
                # content is a variable
                content = eval_value
            else:
                # content contains one or many variables
                content = content.replace(
                    func_content,
                    str(eval_value), 1
                )

        return content


    def _parse_func_return(self, retval):
        retcode = n_step = 0
        retmsg = None
        if(retval != None and isinstance(retval, dict)
                and __RETCODE__ in retval):
            retcode = retval[__RETCODE__]
            if(retcode == 0 and __STEP__ in retval):
                n_step = retval[__STEP__]
            else:
                n_step = 0
            if(__RETMSG__ in retval):
                retmsg = retval[__RETMSG__]
            else:
                retmsg = None
        elif(isinstance(retval, int)):
            retcode = retval
            n_step = 0
            retmsg = None
        elif(retval == None):
            retcode = n_step = 0
            retmsg = None
        else:
            retmsg = "return value type error[" + str(retval) + "]"
            retcode = -1
            n_step = 0
        return retcode, retmsg, n_step

    def do_action(self, action):
        browser=self.browser

        retcode = n_step = 0
        retmsg = None

        self.element = None

        action_before=action.get("BEFORE",None)
        if(action_before != None):
            logger.log_debug("func[%s]" % (action_before))
            self.retval=self._eval_content_with_bindings(action_before)
            retcode, retmsg, n_step = self._parse_func_return(self.retval)
            if(retcode == 0 and n_step != 0):
                return 0
            elif(retcode != 0):
                logger.log_error("Execute[BEFORE FUNC:%s] ERROR[%d][%s]" % (
                    action_before, retcode, retmsg))
                return retcode

        # if(action.has_key("FIND")):
        action_find=action.get("FIND",None)
        if(action_find != None):
            loc_tag=self._eval_content_with_bindings(action["TAG"])
            if(action["FIND"] == "ID"):
                # element=browser.find_element_by_id(action["TAG"])
                self.element = WebDriverWait(browser, 60, 0.5).until(
                    EC.presence_of_element_located((By.ID, loc_tag)))
            elif(action["FIND"] == "CSS"):
                # element=browser.find_element_by_css_selector(action["TAG"])
                self.element = WebDriverWait(browser, 60, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, loc_tag)))
            elif(action["FIND"] == "NAME"):
                # element=browser.find_element_by_name(action["TAG"])
                self.element = WebDriverWait(browser, 60, 0.5).until(
                    EC.presence_of_element_located((By.NAME, loc_tag)))
            elif(action["FIND"] == "TAG"):
                self.element = browser.find_elements_by_tag_name(loc_tag)
                # element=WebDriverWait(browser,60,0.5).until(
                    # EC.presence_of_element_located((By.TAG_NAME, loc_tag)))
            elif(action["FIND"] == "NONE"):
                self.element = None
            else:
                logger.log_error("FIND ERROR[%s]" % (action["STEPNAME"]))
                retcode = -1
                return retcode

        if(action["ACTION"] == "CLICK"):
            self.element.click()
        elif(action["ACTION"] == "CLEAR"):
            self.element.clear()
        elif(action["ACTION"] == "SEND_KEYS"):
            content = self._eval_content_with_bindings(action["CONTENT"])
            self.element.send_keys(content)
        elif(action["ACTION"] == "GET"):
            content=self._eval_content_with_bindings(action["CONTENT"])
            browser.get(content)
        elif(action["ACTION"] == "SWITCH_FRAME"):
            frame_name = ""
            for el in self.element:
                frame_name = el.get_attribute("name")
                if(action["CONTENT"] in frame_name):
                    break
                else:
                    frame_name = ""
            if(frame_name == ""):
                logger.log_error("FRAME[%s] not found" % (action["CONTENT"]))
                retcode = -3
                return retcode
            else:
                browser.switch_to_frame(frame_name)
        else:
            func_name=action["ACTION"]
            logger.log_debug("func[%s]" % (func_name))
            self.retval=self._eval_content_with_bindings(func_name)
            retcode, retmsg, n_step = self._parse_func_return(self.retval)
            if(retcode == 0 and n_step != 0):
                return retcode
            elif(retcode==0 and "ACTION_RETURN" in action and action["ACTION_RETURN"]!=None):
                retvar_list=testcase.extract_variables(action["ACTION_RETURN"])
                data_dic={}
                for i, key in enumerate(retvar_list):
                    if(i in self.retval):
                        data_dic[key.strip()]=self.retval[i]
                    else:
                        raise NameError("ACTION_RETURN error[%s] [%s]" %(func_name, action["ACTION_RETURN"]))
                self.context.bind_extracted_variables(data_dic)
            elif(retcode != 0):
                logger.log_error("Execute[ACTION FUNC:%s] ERROR[%d][%s]" % (
                    func_name, retcode, retmsg))
                return retcode

        # if(action.has_key("AFTER")):
        action_after=action.get("AFTER",None)
        if(action_after != None):
            logger.log_debug("func[%s]" % (action_after))
            self.retval=self._eval_content_with_bindings(action_after)
            retcode, retmsg, n_step = self._parse_func_return(self.retval)
            if(retcode == 0 and n_step != 0):
                return retcode
            elif(retcode != 0):
                logger.log_error("Execute[AFTER FUNC:%s] ERROR[%d][%s]" % (
                    action_after, retcode, retmsg))
                return retcode

        return retcode

    #modified by zhengchun 20180606
    def _parse_steps(self, step_content):
        """ parse steps from list or xls
        @params
            (list) steps: value in list
                step value may be in three types:
                    (1) data list
                    (2) call custom function
                e.g.
                    [
                        {"user_agent": ["iOS/10.1", "iOS/10.2", "iOS/10.3"]},
                        {"username-password": "${parameterize(account.csv)}"},
                        {"app_version": "${gen_app_version()}"}
                    ]
        @return steps in list
        """
        testcase_parser=self.context.testcase_parser

        steps_list = []

        if isinstance(step_content, list):
            # (1) data list
            return step_content
        else:
            steps_list = testcase_parser.eval_content_with_bindings(step_content)
            # e.g. [{'app_version': '2.8.5'}, {'app_version': '2.8.6'}]
            # e.g. [{"username": "user1", "password": "111111"}, {"username": "user2", "password": "222222"}]
            if not isinstance(steps_list, list):
                raise exception.ParamsError("step syntax error!")

        return steps_list

    def init_config(self, config_dict, level):
        """ create/update context variables binds
        @param (dict) config_dict
        @param (str) level, "testset" or "testcase"
        @param (str) context level, testcase or testset
        """
        # convert keys in request headers to lowercase
        config_dict = utils.lower_config_dict_key(config_dict)

        self.context.init_context(level)
        self.context.config_context(config_dict, level)

        request_config = config_dict.get('request', {})
        parsed_request = self.context.get_parsed_request(request_config, level)

        return parsed_request

    def run_test(self, testcase_dict):
        """ run single testcase.
        @param (dict) testcase_dict
            {
                "name": "testcase description",
                "skip": "skip this test unconditionally",
                "times": 3,
                "requires": [],         # optional, override
                "function_binds": {},   # optional, override
                "variables": [],        # optional, override
                "request": {
                    "steps": [
                        {},
                        {}
                    ]
                },
            }
        @return True or raise exception during test
        """
        # parsed_request = self.init_config(testcase_dict, level="testcase")

        try:
            t_level="testcase"
            # convert keys in request headers to lowercase
            config_dict = utils.lower_config_dict_key(testcase_dict)

            self.context.init_context(level=t_level)
            self.context.config_context(config_dict, level=t_level)

            request_config = config_dict.get('request', {})
            self.act_list=self._parse_steps(request_config["steps"])
            self.step=0
            step_len = len(self.act_list)
            while self.step<step_len:
                action=self.act_list[self.step]
                logger.log_info("STEP[%d], ACTION[%s]" %(self.step+1, action))
                self.do_action(action)
                retcode, retmsg, n_step = self._parse_func_return(self.retval)
                if(retcode == 0 and n_step != 0):
                    self.step+=n_step
                elif(retcode!=0):
                    logger.log_error("execute action[%s] error[%s]" %(action, retmsg))
                    break
            
                self.step+=1

        except Exception as e:
            logger.log_error("run do_action error, step[%d], act_list[%s], e[%s]" % (
                self.step+1, self.act_list[self.step], e), exc_info=True)
            retcode=-1
            raise
        finally:
            self._get_windows_img()
            # self.assertEqual(retcode, 0, "retcode[%d], step[%d]" %(retcode, step+1))
        return retcode


def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-l --login")
    print("\t-c --config <filename>")


def get_opts(argv):
    f_login = False
    config = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    d_enc = sys.getdefaultencoding()
    enc = sys.getfilesystemencoding()
    print("filesystem encoding[%s], defaultencoding[%s]" % (enc, d_enc))
    try:
        opts, args = getopt.getopt(
            argv[1:], "hlc:", ["help", "login", "config="])
    except getopt.GetoptError:
        print_usage(argv)
        sys.exit(2)
    for opt, arg in opts:
        # s_t=arg.strip()
        # enc_t=chardet.detect(s_t)["encoding"]
        # if( enc_t!=None and "utf" in enc_t):
        #     s=s_t.decode(enc_t)
        # else:
        #     s=s_t.decode(enc)
        s = arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        elif opt in ("-l", "--login"):
            f_login = True
        elif opt in ("-c", "--config"):
            config = s
    if(config == ""):
        print("-c --config must input")
        sys.exit(3)
    return f_login, config


if __name__ == "__main__":
    from httprunner import task
    f_login = False
    
    # logger.setup_logger("debug")
    if(len(sys.argv) == 1):
        sys.argv += ["-c"] + ["./yusys_new.yaml"]
    print("CMD:[%s]\n" % (sys.argv))
    # testcase_file_path = os.path.join(os.getcwd(), 'tests/data/demo_testset_variables.yml')
    try:
        f_login, testcase_file_path = get_opts(sys.argv)
        testset = testcase.TestcaseLoader.load_test_file(testcase_file_path)
        config_dict=utils.lower_config_dict_key(testset.get("config", {}))
    except Exception as e:
        logger.log_error("load_test_file error[%s]" %e, exc_info=True)
        raise

    logger.setup_logger("info", config_dict["logfile"], console_out=True)
    browser=connect_browser(config_dict)

    if(f_login == True):
        do_login(browser)
        sys.exit(0)

    try:
        suite = task.TestSuite(testset, http_client_session=browser)
    except Exception as e:
        logger.log_error("task.TestSuite testset[%s]" %(testset), exc_info=True)
        raise
        
    # for i, testcase in enumerate(suite):
    #     logger.log_info("now run testcase [%d][%s]" %(i, testcase))
    #     testcase.runTest()

    report_title = config_dict.get("name", "") + '-测试报告'
    desc = '测试报告详情：'
    report_path=gen_report_name(config_dict.get("reportdir", "."), report_title+".html")
    report=open(report_path, 'wb')
    runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
    stderr_handler = logging.StreamHandler(stderr_redirector)
    logging.root.addHandler(stderr_handler)
    result=runner.run(suite)
    logger.log_info("成功[%d] 失败[%d] 错误[%d]" %(result.success_count, result.failure_count, result.error_count))    

    report.close()
    sys.stdout.close()
    sys.stderr.close()
    sys.exit(0)