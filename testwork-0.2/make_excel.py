# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import os
import sys
import getopt
import chardet
import xlrd
import xlwt
# 使用xlutils.copy会报ascii转码错，需要修改xlwt包__init__参数encoding='utf-8'
from xlutils.copy import copy
from xlutils.filter import process, XLRDReader, XLWTWriter
import logging

sys.path.extend([".", "../pylib"])
import logger
from utility import load_dic, find_config, gen_report_name

from httprunner import exception, testcase, utils
from httprunner.runner import Runner

from HTMLTestRunner_zc import HTMLTestRunner, stdout_redirector, stderr_redirector

class makeExecl(Runner):

    # Patch: add this function to the end of xlutils/copy.py
    def _copy2(self, wb):
        '''
        附带样式的copy
    　　　　xlrd打开文件，必须加参数formatting_info=True
        '''

        w = XLWTWriter()
        process(XLRDReader(wb, 'unknown.xls'), w)
        return w.output[0][1], w.style_list


    def _update_content(self):
        rdbook = xlrd.open_workbook(
            'demo_copy2_in.xls', encoding_override="utf-8", formatting_info=True)
        sheetx = 0
        rdsheet = rdbook.sheet_by_index(sheetx)
        wtbook, style_list = self._copy2(rdbook)
        wtsheet = wtbook.get_sheet(sheetx)
        fixups = [(5, 1, 'MAGENTA'), (6, 1, 'CYAN')]
        for rowx, colx, value in fixups:
            xf_index = rdsheet.cell_xf_index(rowx, colx)
            wtsheet.write(rowx, colx, value, style_list[xf_index])
        wtbook.save('demo_copy2_out.xls')


    def _split_params(self, p_list, l_col, l_title, l_content):
        for params in p_list:
            l_col.append(params["COL"])
            l_title.append(params["COL_NAME"])
            content = params["CONTENT"]
            l_content.append(content)


    def _find_col_index(self, l_col, findcol):
        for i in range(len(l_col)):
            if(l_col[i] == findcol):
                return i
            else:
                continue
        return -1


    def _get_src_cell_style(self, style_list, sheet_data, rowx, colx, blank_style):
        if(style_list == None):
            style = blank_style
        else:
            style = style_list[sheet_data.cell_xf_index(rowx, colx)]
        return style


    def _read_sheet(self, book, sheet=None):
        # wb=xlrd.open_workbook(book, formatting_info=True)
        rb = xlrd.open_workbook(book, formatting_info=True)
        if(sheet == None):
            sheet_data = rb.sheets()[0]
            sheet = rb.sheet_names()[0]
        else:
            sheet_data = rb.sheet_by_name(sheet)

        logger.log_info("book[%s]-sheet[%s]: rows[%d], columns[%d]" %
            (book, sheet, sheet_data.nrows, sheet_data.ncols))
        return rb, sheet_data


    def _get_write_sheet(self, targetfile, sheet_name, readbook, f_style):
        if(os.access(targetfile, os.R_OK)):
            rb = xlrd.open_workbook(
                targetfile, encoding_override="utf-8", formatting_info=True)
            workbook = copy(rb)
            for s_n in rb.sheet_names():
                if(s_n == sheet_name):
                    sheet_name += "-1"
        else:
            workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet(sheet_name)
        if(f_style == True):
            w_r_b, style_list = self._copy2(readbook)
        else:
            style_list = None
        return workbook, worksheet, style_list


    def change_sheet(self, params, f_style=False):
        srcfile = params.pop('源文件')
        targetfile = params.pop('目标文件')

        readbook, sheet_data = self._read_sheet(srcfile)
        workbook, worksheet, style_list = self._get_write_sheet(
            targetfile, params["sheetname"], readbook, f_style)

        i_top = params["scope"]["TOP"]
        i_bottom = sheet_data.nrows - params["scope"]["BOTTOM"]
        i_left = params["scope"]["LEFT"]
        i_right = sheet_data.ncols-params["scope"]["RIGHT"]
        add_list = params["add_cols"]
        l_col = []
        l_title = []
        l_content = []
        self._split_params(add_list, l_col, l_title, l_content)

        blank_style = xlwt.XFStyle()

        w_i = 0
        w_j = 0
        for i in range(sheet_data.nrows):
            if(i < i_top):
                logger.log_info("skip top row[%d]" % (i+1))
                continue
            elif(i >= i_bottom):
                logger.log_info("skip bottom row[%d]" % (i+1))
                continue
            w_j = 0
            for j in range(sheet_data.ncols):
                if(j < i_left):
                    continue
                elif(j >= i_right):
                    continue
                idx_col = self._find_col_index(l_col, w_j+1)
                if(idx_col >= 0):
                    if(w_i == 0):
                        worksheet.write(w_i, w_j, l_title[idx_col], self._get_src_cell_style(
                            style_list, sheet_data, i, j, blank_style))
                    else:
                        worksheet.write(w_i, w_j, l_content[idx_col], self._get_src_cell_style(
                            style_list, sheet_data, i, j, blank_style))
                    w_j += 1
                    worksheet.write(w_i, w_j, sheet_data.cell(i, j).value, self._get_src_cell_style(
                        style_list, sheet_data, i, j, blank_style))
                else:
                    worksheet.write(w_i, w_j, sheet_data.cell(i, j).value, self._get_src_cell_style(
                        style_list, sheet_data, i, j, blank_style))
                w_j += 1
            for idx in range(len(l_col)):
                if(w_j <= l_col[idx]):
                    if(w_i == 0):
                        worksheet.write(w_i, l_col[idx]-1, l_title[idx], self._get_src_cell_style(
                            style_list, sheet_data, i, j, blank_style))
                    else:
                        worksheet.write(w_i, l_col[idx]-1, l_content[idx], self._get_src_cell_style(
                            style_list, sheet_data, i, j, blank_style))
                    w_j = l_col[idx]
            w_i += 1
        workbook.save(targetfile)
        logger.log_info("target[%s]-sheet[%s]: rows[%d], columns[%d]" %
            (targetfile, worksheet.name, w_i, w_j))

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
                    "scrope": {BOTTOM: 2, LEFT: 1, RIGHT: 1, TOP: 3},
                    "add_cols": [
                        {COL: 1, COL_NAME: 月份, CONTENT: "201712"},
                        {COL: 35, COL_NAME: 口径, CONTENT: "管理"}
                    ]
                },
                sheetname: 项目-${口径},
                源文件: $workdir/${月份}/$名称-$口径-$月份.xls,
                目标文件: $workdir/${月份}/部门损益明细表-整理后-$月份.xls
            }
        @return True or raise exception during test
        """
        parsed_request = self.init_config(testcase_dict, level="testcase")

        try:
            logger.log_info("%s" %(parsed_request))
            self.change_sheet(parsed_request)
        except Exception as e:
            logger.log_error("run error[%s]" % (parsed_request), exc_info=True)
            # raise

def print_usage(argv):
    print("Usage: ", argv[0])
    print("\t-h --help")
    print("\t-c --config <config filename>")

def get_opts(argv):
    configfile = ""

    if(len(argv) == 1):
        print_usage(argv)
        sys.exit(1)

    d_enc = sys.getdefaultencoding()
    enc = sys.getfilesystemencoding()
    print("filesystem encoding[%s], defaultencoding[%s]" % (enc, d_enc))
    try:
        opts, args = getopt.getopt(argv[1:], "hc:", [
                                   "help", "config="])
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
        # print("CMD encoding[%s][%s]" %(enc,chardet.detect(s)))
        s = arg.strip()
        if opt in ("-h", "--help"):
            print_usage(argv)
            sys.exit(1)
        elif opt in ("-c", "--config"):
            configfile = s
    if(configfile == ""):
        print_usage(argv)
        sys.exit(3)
    return configfile


if __name__ == "__main__":
    from httprunner import task
    
    # 测试用
    if(len(sys.argv) == 1):
        sys.argv += ["-c"] + ["make-execl.yaml"]
    print("CMD:[%s]\n" % (sys.argv))
    try:
        # testcase_file_path = os.path.join(os.getcwd(), 'tests/data/demo_testset_variables.yml')
        testcase_file_path = get_opts(sys.argv)
        testset = testcase.TestcaseLoader.load_test_file(testcase_file_path)
        config_dict=utils.lower_config_dict_key(testset.get("config", {}))
    except Exception as e:
        logger.log_error("task.TestSuite file[%s]" %(testcase_file_path), exc_info=True)
        raise

    # for i, testcase in enumerate(suite):
    #     logger.log_info("now run testcase [%d][%s]: {}" %(i, testcase))
    #     testcase.runTest()
    logger.setup_logger("info", config_dict["logfile"], console_out=True)
    suite = task.TestSuite(testset)

    report_title = config_dict.get("name", "") + '-测试报告'
    desc = '测试报告详情：'
    report_path=gen_report_name(config_dict.get("reportdir", "."), report_title+".html")
    report=open(report_path, 'wb')
    runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
    stderr_handler = logging.StreamHandler(stderr_redirector)
    # stderr_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)-8s %(filename)s.%(funcName)s().%(lineno)dL %(message)s"))
    logging.root.addHandler(stderr_handler)
    result=runner.run(suite)
    logger.log_info("成功[%d] 失败[%d] 错误[%d]" %(result.success_count, result.failure_count, result.error_count))    
    
    report.close()
        