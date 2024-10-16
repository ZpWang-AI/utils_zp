def run_multitasks(tasks):
    # import multiprocessing as mp
    import pathos.multiprocessing as mp
    from functools import partial
    
    results = [None]*len(tasks)

    def _get_target(func, args, kwargs, fid):
        def _new_func():
            res = func(*args, **kwargs)
            results[fid] = res
        return _new_func

    thread_tasks = []
    pool = mp.ProcessPool()
    for fid, (func, args, kwargs) in enumerate(tasks):
        cur_thread = pool.apipe(
            f=_get_target(func, args, kwargs, fid),
            # daemon=False,
        )
        # cur_thread.start()
        thread_tasks.append(
            cur_thread
        )
    pool.close()
    pool.join()
    results = [p.get()for p in thread_tasks]
    return results
