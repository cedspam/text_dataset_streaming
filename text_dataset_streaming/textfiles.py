# -*- coding: utf-8 -*-
import requests
import smart_open
# -*- coding: utf-8 -*-

import random
import logging
import functools
import itertools

import unicodedata
from .bufgen import threaded_bufgen,bufgen_decorator
logging.captureWarnings(True)




def unwrap_lines(txt2,cols=40):
  txt3=""
  for t in txt2.split("\n"):
    txt3+=t
    if  len(t)<cols:
      txt3+="\n"
    elif unicodedata.category(t[-1])[0]=="P" and t[-1] not in ",_-":
      txt3+="\n"
  return txt3


def splitgen(textgen):
  for t in textgen:
    for l in t.split("\n"):
      l=l.strip()
      if len(l)>0:
        yield l


def split_ligne(t,chunk_size=int(32e6),minsplit=4096):
    chunk_size=int(chunk_size)
    if minsplit>chunk_size*0.8:
        minsplit=int(chunk_size*0.8-1)

    texte=""
    l=t[minsplit:chunk_size].rsplit("\n",1)
    if len(l)>1:
          texte1,reste=l
    else:
          texte=l[0]
          reste=""
    texte=t[:minsplit]+texte
    reste+=t[chunk_size:]
    if (len(texte)+len(reste))<chunk_size:
      if len(reste)>0 and reste[-1]=="\n":
          texte+=reste
          reste=""
    return texte,reste

#@bufgen_decorator
def url_textgen(u,chunk_size=int(32e6),encoding="utf8",minsplit=30,cols=35):
    reste=""
    if chunk_size*0.55<minsplit:
       minsplit= int(chunk_size*0.6)

    try:
        with smart_open.open(u,
                 encoding=encoding,errors="ignore") as f:
          t=f.read(chunk_size)
          texte,reste=split_ligne(t,chunk_size*0.8,minsplit=minsplit)
          while len(t)>0:
            yield unwrap_lines(texte,cols)
            read_size=chunk_size-len(reste)
            if read_size>0:
              t=f.read(read_size)
            else:
              t=""
            texte,reste=split_ligne(reste+t,int(chunk_size*0.8),
                                    minsplit=minsplit)

        yield unwrap_lines(texte,cols)

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except GeneratorExit:
        raise GeneratorExit
    except:
        logging.exception("exception url %s",u)

def urllist_to_textgen_list(urls,chunk_size=int(32e6),encoding="utf8",
                            randomize=True,minsplit=30,cols=35):
    if randomize:
        urls=list(urls)
        random.shuffle(urls)
    textgen_func=functools.partial(url_textgen,chunk_size=chunk_size,
                                   encoding=encoding,minsplit=minsplit,cols=cols)
    return map(textgen_func,urls)


#@bufgen_decorator
def urllist_textgen(urls,chunk_size=2048,encoding="utf8",randomize=True,minsplit=30,cols=35):
    iters=urllist_to_textgen_list(urls,chunk_size=chunk_size,
                                   encoding=encoding,randomize=randomize,minsplit=minsplit,cols=cols)
    return itertools.chain.from_iterable(iters)



