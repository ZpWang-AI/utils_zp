from utils_zp import *


a = AttrDict({'a':1}, b=2)
a.c = 3
a['d'] = 4
# a = AttrDict(one=1)

a.e = [AttrDict(f=AttrDict(g=5))]

print(a)
print(a.d)
print(type(a.e[0]))
print(type(a.e[0].f))