# coding=utf-8   //这句是使用utf8编码方式方法， 可以单独加入python头使用
import sys
import functools
import logging

# logger=logging.getLogger(__name__)

def debug(f=None, *, level=logging.DEBUG):
    if f is None:
        return functools.partial(debug, level=level)

    @functools.wraps(f) # we tell wraps that the function we are wrapping is f
    def log_f_as_called(*args, **kwargs):
        logging.log(level, f'{f} was called with arguments={args} and kwargs={kwargs}')
        value = f(*args, **kwargs)
        logging.log(level, f'{f} return value {value}')
        return value

    return log_f_as_called

@debug
# @debug(level=logging.INFO)
def hello(argc, argv):
    print(f'{hello}, argc={argc}, argv={argv}')

if __name__ == "__main__":
    print(f'{__name__} was called with arguments={len(sys.argv)}, {sys.argv}')
    logging.getLogger().setLevel(logging.INFO)
    hello(2, ["name", "age"])
