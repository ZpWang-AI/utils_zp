from utils_zp import *


_input = []
_output = {}

# with IgnoreException(
#     print_exc=True
# ):
#     1/0
with ExceptionManager(
    exception_log_func=builtin_print,
    ignore_error=False
):
    1/0

print(123)