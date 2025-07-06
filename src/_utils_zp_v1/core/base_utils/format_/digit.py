class format_int:
    """
    examples:
        123,456,789
        12,345,678
        1,234,567
        -123,456,789
    """
    def __new__(cls, _int) -> str:
        return cls._func(_int)
    
    @staticmethod
    def _func(_int):
        _int = str(_int)
        if _int[0] == '-':
            neg_flag = True
            _int = _int[1:]
        else:
            neg_flag = False
        _str_list = [_int[max(0, p-3):p]for p in range(len(_int), 0, -3)]
        _str = ','.join(_str_list[::-1])
        if neg_flag:
            _str = '-'+_str
        return _str
    

class format_float:
    """
    examples:
        -1.234e+8
        +1.200e+1
        +1.000e0
        +1.234e-11
        0.0
    """
    def __new__(cls, _float) -> str:
        return cls._func(_float)
    
    @staticmethod
    def _func(_float):
        if _float > 0:
            pn_sign = '+'
        elif _float < 0:
            pn_sign = '-'
            _float = -_float
        else:
            return '0.0'
        num_e = 0
        pn_sign_e = ''
        while _float < 1:
            pn_sign_e = '-'
            _float *= 10
            num_e += 1
        while _float >= 10:
            pn_sign_e = '+'
            _float /= 10
            num_e += 1
        return f'{pn_sign}{_float:.3f}e{pn_sign_e}{num_e}'


if __name__ == '__main__':
    print(format_int(123456789))
    print(format_int(12345678))
    print(format_int(1234567))
    print(format_int(-123456789))
    
    print(format_float(-123456789))
    print(format_float(12))
    print(format_float(1))
    print(format_float(0))
    print(format_float(0.0000000000123456789))