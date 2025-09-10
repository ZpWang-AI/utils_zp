from utils_zp import *


_input = []
_output = {}

# with IgnoreException(
#     print_exc=True
# ):
#     1/0
with ExceptionManager(
    exception_log_func=builtin_print,
    ignore_error=True,
    exception_log_file=path(__file__).parent/'~exception.log'
):
    1/0

print(123)
