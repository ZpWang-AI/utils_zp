from utils_zp import *


@BaseDecoratorCreator(
    print_info=True,
    print_running_time=True,
    print_input=True,
    print_output=True,
    
    exception_log_file=path(__file__).parent/'~tmp.log',
    # exception_info='123error info',
    ignore_error=True,
    default_return='default return'
)
def abc(a,b,c):
    print(a+b+c)
    1/0
    

abc(1,2,3)