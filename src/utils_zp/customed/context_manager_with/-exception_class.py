from utils_zp import ExceptionManager


class CustomExc(ExceptionManager):
    def __exit__(self, exc_type, exc_value, traceback_):
        # if issubclass(exc_type, ZeroDivisionError):
        #     print(11)
        #     return True
        return False
        return super().__exit__(exc_type, exc_value, traceback_)
    

if __name__ == '__main__':
    with CustomExc():
        1/0
        1/1
        pass
        