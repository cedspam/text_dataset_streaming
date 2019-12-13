# -*- coding: utf-8 -*-
import threading
import queue
import collections.abc
import itertools
import random
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


    while task.is_alive():
      with lock:
        try:
            yield q.get(timeout=1)
        except queue.Empty:
            pass

def bufgen_decorator(func,*args,maxsize=3,**kvargs):
    def closure(*args,**kvargs):
        gen=func(*args,**kvargs)
        return threaded_bufgen(gen,maxsize)
    if hasattr(func,"__doc__"):
        closure.__doc__=func.__doc__
    closure.__name__=func.__name__
    return closure

def multisource_gen_concat(genlist,randomize=True,buffsisze=2):
    task_list=[]
    lock = threading.Lock()
    queue_list=[]
    def wrap(gen,q):
       for t in gen:
           q.put(t)
    for i  in range(len(genlist)):
        q=queue.Queue(maxsize=buffsisze)
        queue_list.append(q)
        gen=genlist[i]

        if isinstance(gen,collections.abc.Iterable):
            if  all(isinstance(a,str) for a in gen):
                gen=iter(gen)
            elif all(isinstance(a,gen,collections.abc.Iterator) for a in gen):
                gen=itertools.chain.from_iterable(gen)

        elif not isinstance(gen,collections.abc.Iterator):
            gen=itertools.chain.from_iterable(gen)

        task=threading.Thread(target=wrap,args=(gen,q) )
        task.start()
        task_list.append(task)
    while any(task.is_alive() for task in task_list):
        if randomize:
            random.shuffle(queue_list)
        for q in queue_list:
            try:
                    while not q.empty() :
                        with lock:
                            yield q.get( timeout=0.01)
            except queue.Empty:
                continue

def threadsafe_wrap(gen):
    lock = threading.Lock()
    for i in gen:
        with lock:
            yield i









