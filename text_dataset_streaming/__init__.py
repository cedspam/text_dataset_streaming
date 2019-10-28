# -*- coding: utf-8 -*-
import threading
import queue

from .textfiles import urllist_textgen,opus_mono_textgen
from .wiki import wiki_article_generator



def threaded_bufgen(gen,maxsize=2):
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


def bufgen_decorator(func,*args,maxsize=2,**kvargs):
    def closure(*args,**kvargs):
        gen=func(*args,**kvargs)
        return threaded_bufgen(gen,maxsize)
    return closure


