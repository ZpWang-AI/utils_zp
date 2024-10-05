def run_multitasks(tasks):
    import threading
    from functools import partial
    
    results = [None]*len(tasks)

    def _get_target(func, args, kwargs, fid):
        def _new_func():
            res = func(*args, **kwargs)
            results[fid] = res
        return _new_func

    thread_tasks = []
    for fid, (func, args, kwargs) in enumerate(tasks):
        cur_thread = threading.Thread(
            target=_get_target(func=func, fid=fid, args=args, kwargs=kwargs),
            daemon=False,
        )
        cur_thread.start()
        thread_tasks.append(
            cur_thread
        )
    for task in thread_tasks:
        task:threading.Thread
        task.join()
    return results