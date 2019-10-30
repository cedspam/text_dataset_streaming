# -*- coding: utf-8 -*-
import threading
import queue

def threaded_bufgen(gen,maxsize=3):
    """
        queue buffer of maxsize of gen iterator
    """
    lock = threading.Lock()
    q=queue.Queue(maxsize=2)
    def wrap(gen=gen):
        for result in gen:
            q.put(result)


    task=threading.Thread(target=wrap,args=(gen,) )
    task.start()


    while True:
      with lock:
        yield q.get()


def bufgen_decorator(func,*args,maxsize=3,**kvargs):
    def closure(*args,**kvargs):
        gen=func(*args,**kvargs)
        return threaded_bufgen(gen,maxsize)
    if hasattr(func,"__doc__"):
        closure.__doc__=func.__doc__
    closure.__name__=func.__name_
    return closure



