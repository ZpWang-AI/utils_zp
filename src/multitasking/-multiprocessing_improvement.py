import marshal
import multiprocessing
import pickle
import types
from functools import partial


class A:
    def __init__(self, a):
        self.a = a


def main():
    x = A(1)

    def internal_func(c):
        return x.a + c

    with multiprocessing.Pool(5) as pool:
        print(internal_func_map(pool, internal_func, [i for i in range(10)]))


def internal_func_map(pool, f, gen):
    closure = f.__closure__
    marshaled_func = marshal.dumps(f.__code__)
    pickled_closure = pickle.dumps(tuple(x.cell_contents for x in closure))
    return pool.map(partial(run_func, marshaled_func=marshaled_func, pickled_closure=pickled_closure), gen)


def run_func(*args, **kwargs):
    marshaled_func = kwargs.pop("marshaled_func")
    func = marshal.loads(marshaled_func)
    pickled_closure = kwargs.pop("pickled_closure")
    closure = pickle.loads(pickled_closure)

    restored_f = types.FunctionType(func, globals(), closure=create_closure(func, closure))
    return restored_f(*args, **kwargs)


def create_closure(func, original_closure):
    indent = " " * 4
    closure_vars_def = f"\n{indent}".join(f"{name}=None" for name in func.co_freevars)
    closure_vars_ref = ",".join(func.co_freevars)
    dynamic_closure = "create_dynamic_closure"
    s = (f"""
def {dynamic_closure}():
    {closure_vars_def}
    def internal():
        {closure_vars_ref}
    return internal.__closure__
""")
    exec(s)
    created_closure = locals()[dynamic_closure]()
    for closure_var, value in zip(created_closure, original_closure):
        closure_var.cell_contents = value
    return created_closure


if __name__ == "__main__":
    main()
