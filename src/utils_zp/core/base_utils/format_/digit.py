class format_int:
    def __new__(cls, _int) -> str:
        return cls._func(_int)
    
    @staticmethod
    def _func(_int):
        _int = str(_int)
        _str_list = [_int[max(0, p-3):p]for p in range(len(_int), 0, -3)]
        _str = ','.join(_str_list[::-1])
        return _str
    

class format_float:
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
            pn_sign_e = '+'
            _float *= 10
            num_e += 1
        while _float >= 10:
            pn_sign_e = '-'
            _float /= 10
            num_e += 1
        return f'{pn_sign}{_float:.3f}e{pn_sign_e}{num_e}'


if __name__ == '__main__':
    print(format_int(112301230121))
    print(format_int(12301230121))
    print(format_int(2301230121))
    print(format_int(301230121))
    print(format_float(-1213123123))
    print(format_float(0.00000000001213123123))