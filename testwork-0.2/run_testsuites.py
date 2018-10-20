import os
import sys
import getopt
from time import sleep
import time
import copy
import logging

sys.path.extend([".", "../pylib"])
import logger

from httprunner import exception, testcase, utils, task

from HTMLTestRunner_zc import HTMLTestRunner, stdout_redirector, stderr_redirector

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-c --config <yaml1,yaml2,...>")
    print("\t-l --log <logfile>")

def get_opts(argv):
    configfile = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    d_enc = sys.getdefaultencoding()
    enc = sys.getfilesystemencoding()
    print("filesystem encoding[%s], defaultencoding[%s]" % (enc, d_enc))
    try:
        opts, args = getopt.getopt(argv[1:], "hc:l:", [
                                   "help", "config=", "log="])
    except getopt.GetoptError:
        print_usage(argv)
        sys.exit(2)
    for opt, arg in opts:
        s = arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        elif opt in ("-c", "--config"):
            configfile = s.split(',')
            configfile=[x.strip() for x in configfile]               
        elif opt in ("-l", "--log"):
            logfile=s           
    if(configfile == ""):
        print_usage(argv)
        sys.exit(3)
    return configfile, logfile

if __name__=="__main__":
    # 测试用
    if(len(sys.argv) == 1):
        sys.argv += ["-c"] + ["yusys_new.yaml, make-execl.yaml"] + ["-l"] + ["X:/TEMP/report/test.log"]
    print("CMD:[%s]\n" % (sys.argv))
    try:
        testcase_file_path_list, logfile = get_opts(sys.argv)
        task_suite = task.init_task_suite(testcase_file_path_list)
    except exception.TestcaseNotFound:
        logger.log_error("Testcases not found in {}".format(testcase_file_path_list), exc_info=True)
        sys.exit(1)
    
    logger.setup_logger("debug", logfile, console_out=True)
    logger.log_info("tasksuite:{}".format(task_suite))
