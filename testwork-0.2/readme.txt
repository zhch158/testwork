testwork.utils.py:
	1.目录名称修改为testwork
	2.修改deep_update_dict()增加对(list, tuple)的支持
	3.修改is_function()增加types.BuiltinFunctionType函数类型
	
testwork.testcase.py:
	1.目录名称修改为testwork
	2.import sys
	3.修改针对变量，函数的正则表达式，允许变量的形式为${VAR} or $VAR，函数中的变量可以有双引号，/等
	4.修改extract_variables()，以匹配2种变量形式
	5.修改load_test_file()，在config节中可以配置自定义Runner
	6.修改parse_parameters()，增加参数parser_handle，指定使用testrunner.context.testcase_parser
	7.修改_eval_content_variables()，适应变量（${VAR}, $VAR）的赋值

testwork.task.py:
	1.目录名称修改为testwork
	2.修改TestSuite.__init__()，可以实例化自定义Runner；
	3.参数变量化使用testrunner.context.testcase_parser

testwork.runner.py:
	1.目录名称修改为testwork
	2.修改init_config()，去掉http_client_session部分（应该不去掉，自定义Runner中要重载init_config）

testwork.logger.py:
	1.import os
	2.修改setup_logger()，增加参数console_out=True，允许输出文件的同时输出终端，终端彩色显示依靠log_color
	3.修改log_with_color()，输出内容是否彩色由formatter控制

testwork.context.py:
	1.目录名称修改为testwork
	2.修改init_context()，去掉自动装在built_in
	3.
	