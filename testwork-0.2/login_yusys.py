#coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import chardet
import os,sys,getopt
sys.path.extend([".", "../pylib"])
import logger
from utility import dump_dic
from httprunner import utils

def do_login(browser):
    browser.get('http://it.yusys.com.cn/yusys/login.html')
    browser.find_element_by_id("loginname").send_keys("zhengchun")
    browser.find_element_by_id("password").send_keys("Zhch1234")
    browser.find_element_by_id("checkcode").clear()
    # enc=sys.getfilesystemencoding()
    # prompt_str=unicode("请在浏览器中输入验证码，返回命令窗口，按任意键继续...").encode(enc)
    prompt_str="请在浏览器中输入验证码，返回命令窗口，按任意键继续..."
    input(prompt_str)
    browser.find_element_by_id("login_btn").click()
    return 0

def connect_browser(conf_dict):
    webfile=conf_dict["session"]
    filedir=conf_dict["downloaddir"]
    firefoxprofile=conf_dict["firefoxprofile"]
    logger.log_info("webfile[%s] download[%s] FirefoxProfile[%s]" %(webfile, filedir, firefoxprofile))

    profile = webdriver.FirefoxProfile(os.path.abspath(firefoxprofile))
    profile.set_preference('browser.download.dir',os.path.abspath(filedir))
    profile.set_preference('browser.download.folderList',2)
    profile.set_preference('browser.download.manager.showWhenStarting',False)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk','application/octet-stream ,application/zip,application/kswps,application/pdf')
    # driver =webdriver.Firefox(firefox_profile=profile)

    driver = webdriver.remote.webdriver.WebDriver(command_executor="http://127.0.0.1:4444",
        desired_capabilities=DesiredCapabilities.FIREFOX,
        browser_profile=profile)  
    #调用下列方法，myFireFox无法得到Handle
    # driver = webdriver.Remote(command_executor="http://127.0.0.1:4444",
    #     desired_capabilities=DesiredCapabilities.FIREFOX,
    #     browser_profile=profile)  
    driver.implicitly_wait(20)
    do_login(driver)

    logger.log_info("url[%s] session_id[%s] keep_alive[%s]" %(driver.command_executor._url, driver.session_id, driver.command_executor.keep_alive))

    params = {}
    params["session_id"] = driver.session_id
    params["server_url"] = driver.command_executor._url
    params["capabilities"] = driver.capabilities
    dic_list=list()
    dic_list.append(params)
    dump_dic(webfile, dic_list)

    return driver

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-c --config <filename>")

def get_opts(argv):
    config=""

    if(len(argv)==1):
        print_usage(argv)
        sys.exit(1)

    d_enc=sys.getdefaultencoding()
    enc=sys.getfilesystemencoding()
    print("filesystem encoding[%s], defaultencoding[%s]" %(enc, d_enc))
    try:
        opts, args = getopt.getopt(argv[1:],"hc:",["help",  "config="])
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
        s=arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        elif opt in ("-c", "--config"):
            config = s
    return config

if __name__ == "__main__":
    #测试用
    if(len(sys.argv)==1):
        sys.argv+=["-c"] + ["./yusys_new.yaml"]
    configfile = get_opts(sys.argv)
    config_dic=utils.FileUtils.load_file(configfile)
    config_dic=utils.lower_dict_keys(config_dic[0]["config"])
    logger.setup_logger("info", config_dic["logfile"])
    logger.log_debug(str(config_dic))
    
    connect_browser(config_dic)

    sys.stdout.close()
    sys.stderr.close()
    sys.exit(0)

    # driver.quit()