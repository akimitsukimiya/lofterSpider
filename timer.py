import multiprocessing
import time
pool = multiprocessing.Pool(1)

def timeit( func, *args,limit = 5, **kwargs):
    runner = pool.apply_async(func, args, kwargs)
    try:
        rst = runner.get(limit)
        return rst
    except multiprocessing.context.TimeoutError:
        print('Something must be wrong! Time out!')
        return 'timeout'

    

    
