class LazyCall:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.val = None
    
    def __call__(self):
        if self.val is None:
            self.val = self.func(*self.args, **self.kwargs)
        return self.val


if __name__ == '__main__':
    _lazycall = LazyCall(lambda x:x+1, 123)
    print(_lazycall())