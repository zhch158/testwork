import unittest
import sys
import time
import logging
from webdriver import myFirefox
# from webdriver.myFirefox.support.ui import WebDriverWait
sys.path.append("..")
from pylib.utility import gen_report_name, load_config, load_dic, load_xls
#导入HTMLTestRunner库，这句也可以放在脚本开头
from pylib.HTMLTestRunner_zc import HTMLTestRunner, stdout_redirector, stderr_redirector
from ex_selenium_script import do_action, do_login, get_opts

class MyTestCase(unittest.TestCase):  

    @classmethod
    def setUpClass(cls):
        print("Start class[%s]" %cls.__name__)
   
    # def getTest(self, arg1, arg2):#定义的函数，最终生成的测试用例的执行方法  
    #     print("[FUNC:%s] [arg1:%s] [arg2:%s]" %(self._testMethodName, arg1, arg2))  
    #     self.assertEqual(2, 2)
  
    @staticmethod    
    def getTestFunc(browser, testcase_list, data, conf_dic):  
        def func(self):  
            retcode, step=do_action(browser, testcase_list, data, conf_dic)
            self.assertEqual(retcode, 0, "retcode[%d], step[%d]" %(retcode, step+1))
        return func
    
    @classmethod
    def tearDownClass(cls):
        print("[testMethod:%s] finished" %cls.__name__)
           
def __generateTestCases(cls_name, suite, browser, testcase_list, testdata_list, conf_dic):
    new_class = type(cls_name, (MyTestCase,), {})
    for i, testdata in enumerate(testdata_list):
        test_func="test_case_"+str(i+1)
        setattr(new_class, test_func, MyTestCase.getTestFunc(browser, testcase_list, testdata, conf_dic))#通过setattr自动为TestCase类添加成员方法，方法以“test_func_”开头  
        suite.addTest(new_class(test_func))
  
if __name__ =='__main__':  
    f_login=False
    configfile=filedir=y_m=webfile=testfile=reportdir=""
    if(len(sys.argv)==1):
        # sys.argv+=["-l"] + ["-t"] + ["syxm-gl.json"] + ["-d"] + ["2017-11"]
        sys.argv+= ["-c"] + ["yusys.yaml"]
        print("CMD:[%s]\n" %(sys.argv))
    f_login, configfile = get_opts(sys.argv)
    conf_dic, logger=load_config(configfile)
    print(type(conf_dic))
    print(conf_dic)

    webfile=conf_dic["session"]
    filedir=conf_dic["downloaddir"]
    reportdir=conf_dic["reportdir"]
    logger.debug("webfile[%s] download[%s] reportdir[%s]" %(webfile, filedir, reportdir))
    
    dic_list=list()
    load_dic(webfile, dic_list)
    params=dic_list[0]
    logger.debug(params)
    browser = myFirefox.myWebDriver(capabilities=params["capabilities"], service_url=params["server_url"],
        session_id=params["session_id"])
    logger.debug(browser.capabilities)
    logger.debug(browser.command_executor._url)
    logger.debug(browser.session_id)

    if(f_login==True):
        do_login(browser)
        sys.exit(0)

    report_title = '模块测试报告'
    desc = '测试报告详情：'
    report_path=gen_report_name(reportdir, "report.html")
    report=open(report_path, 'wb')
    runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
    stderr_handler = logging.StreamHandler(stderr_redirector)
    logger.addHandler(stderr_handler)
    # logging.basicConfig(stream=stderr_redirector)
    # runner=unittest.TextTestRunner()
    suite=unittest.TestSuite()

    # for key, value in conf_dic["TESTSUITES"].iteritems():
    testsuites=conf_dic["TESTSUITES"]
    for key, value in testsuites.items():
        logger.info("开始处理案例集[%s][%s]" %(key, value))
        testfile=value["testfile"]
        testcase=value["testcase"]
        testdata=value["testdata"]

        testcase_list=list()
        testcase_list=load_xls(testfile, testcase)
        for i, data in enumerate(testcase_list):
            logger.debug("STEP[%d][%s]" %(i,data))

        testdata_list=list()
        testdata_list=load_xls(testfile, testdata)
        logger.info("测试数据[\n%s\n]" %(str(testdata_list)))

        cls_name="Test_CLASS_"+testcase
        __generateTestCases(cls_name, suite, browser, testcase_list, testdata_list, conf_dic)

    result=runner.run(suite)
    logger.info("成功[%d] 失败[%d] 错误[%d]" %(result.success_count, result.failure_count, result.error_count))    

    report.close()
    sys.stdout.close()
    sys.stderr.close()
    sys.exit(0)
