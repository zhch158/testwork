# encoding: utf-8

import logging
import sys, os, io, traceback

from colorama import Back, Fore, Style, init
from colorlog import ColoredFormatter

init(autoreset=True)

log_colors_config = {
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red',
}

def setup_logger(log_level, log_file=None, console_out=True):
    """setup root logger with ColoredFormatter."""
    level = getattr(logging, log_level.upper(), None)
    if not level:
        color_print("Invalid log level: %s" % log_level, "RED")
        sys.exit(1)

    # hide traceback when log level is INFO/WARNING/ERROR/CRITICAL
    if level >= logging.INFO:
        # sys.tracebacklimit = 0
        pass

    if(console_out==True):
        formatter = ColoredFormatter(
            #modified by zhengchun 20180607 message的颜色由log_color控制
            # u"%(log_color)s%(bg_white)s%(levelname)-8s%(reset)s %(asctime)s - %(filename)s.%(funcName)s().%(lineno)dL %(log_color)s%(message)s",
            u"%(log_color)s%(levelname)-8s%(reset)s %(asctime)s - %(log_color)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors=log_colors_config
        )

        handler_console = logging.StreamHandler()
        handler_console.setFormatter(formatter)
        logging.root.addHandler(handler_console)

    if log_file:
        formatter_file = ColoredFormatter(
            u"%(asctime)s - %(levelname)-8s - %(message)s",
            reset=False,
            log_colors={}
        )

        head, tail=os.path.split(log_file)
        if head and tail and not os.path.exists(head):
            os.makedirs(head)
        handler_file = logging.FileHandler(log_file, encoding="utf-8")
        handler_file.setFormatter(formatter_file)
        logging.root.addHandler(handler_file)

    logging.root.setLevel(level)

def coloring(text, color="WHITE"):
    fore_color = getattr(Fore, color.upper())
    return fore_color + text

def color_print(msg, color="WHITE"):
    fore_color = getattr(Fore, color.upper())
    print(fore_color + msg)

def _findCaller(stack_info=False):
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    """
    f = logging.currentframe()
    #On some versions of IronPython, currentframe() returns None if
    #IronPython isn't run with -X:Frames.
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)", None
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == logging._srcfile:
            f = f.f_back
            continue
        sinfo = None
        if stack_info:
            sio = io.StringIO()
            sio.write('Stack (most recent call last):\n')
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]
            sio.close()
        rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
        break
    return rv

def log_with_color(level):
    """ log with color by different level
    """
    def wrapper(text, exc_info=False):
        #modified by zhengchun 20180607
        # color = log_colors_config[level.upper()]
        # getattr(logging, level.lower())(coloring(text, color))

        # fn, lno, func, sinfo = _findCaller(stack_info=False)
        # out_text="[F:" + os.path.basename(fn) + "] [M:" + func + "] [L:" + str(lno) + "] - " + text
        sinfo=None
        f=sys._getframe().f_back
        out_text="[F:" + os.path.basename(f.f_code.co_filename) + "] [M:" + f.f_code.co_name + "] [L:" + str(f.f_lineno) + "] - " + text
        if(exc_info):
            sio = io.StringIO()
            sio.write('Stack (most recent call last):\n')
            traceback.print_stack(f, file=sio)
            sinfo = sio.getvalue()
            if sinfo[-1] == '\n':
                sinfo = sinfo[:-1]
            sio.close()
        out_text += "\n" + str(sinfo)

        getattr(logging, level.lower())(out_text)

    return wrapper

log_debug = log_with_color("debug")
log_info = log_with_color("info")
log_warning = log_with_color("warning")
log_error = log_with_color("error")
log_critical = log_with_color("critical")

if __name__=="__main__":
    setup_logger("debug", "./test.log")
    log_debug("this is debug[%s]" %(os.path.curdir))
    log_info("this is info")
    log_warning("this is warning")
    log_error("this is error, curdir[%s]" %os.curdir, exc_info=True)