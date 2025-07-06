from utils_zp import *


# @dataclasses.dataclass
class B:
    b:str = '123aaaaaaaaaaaaaaa'

# @config_args
@config_args
# class A(ConfigArgs):
@dataclasses.dataclass
# class A(ConfigArgs):
class A:
    '''
    123123
    '''
# class A:
    # ========== 123 =========================
    part1:str = '123'
    a:int = 123
    b:int ='213'

    def show(self):
        self.abbbb = dataclasses.Field('adf', 'adf', True, True, True, True, {}, True)

        self.a = 123123213
        print(self)

# A:ConfigArgs
# A().format_part_in_file(__file__)
# print(A().dic)
# print(A())
# print(A().dic)

# B = dataclasses.dataclass(A)
# sb = B()

sa = A()
sb = A(**sa.dic)
print(sa,sb)
exit()
# sa.set_create_time('123')
print(ConfigArgs())
# sa:ConfigArgs
sa.format_part_in_file(__file__)
print(sa)
# sa.show()
# # sa.format_part()
# print(type(sa))
# print(sa)
# A()._po

