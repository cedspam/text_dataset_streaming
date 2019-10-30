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

def unwrap_lines(txt2,cols=40):
  txt3=""
  for t in txt2.split("\n"):
    txt3+=t
    if  len(t)<cols:
      txt3+="\n"
    elif unicodedata.category(t[-1])[0]=="P" and t[-1] not in ",_-":
      txt3+="\n"
  return txt3





def split_ligne(t,chunk_size=int(32e6),minsplit=4096):
    lreste=chunk_size-len(t)
    lreste=int(lreste)

    texte=""
    l=t[minsplit:].rsplit("\n",1)
    if len(l)>1:
          texte1,reste=l
    else:
          texte=l[0]
          reste=""
    texte=t[:minsplit]+texte
    if len(reste)>0 and reste[-1]=="\n":
        texte+=reste
        reste=""
    return texte,reste

#@bufgen_decorator
def url_textgen(u,chunk_size=int(32e6),encoding="utf8",minsplit=4096,cols=35):
    reste=""
    if chunk_size<minsplit:
       minsplit= chunk_size

    try:
        with smart_open.open(u,
                 encoding=encoding,errors="ignore") as f:
          t=f.read(chunk_size)
          texte,reste=split_ligne(t,chunk_size*0.8)
          while len(t)>0:
            yield unwrap_lines(texte,cols)
            t=f.read(chunk_size)
            texte,reste=split_ligne(reste+t,int(chunk_size*0.8),
                                    minsplit=minsplit)
        if len(reste)>0:
            yield unwrap_lines(reste,cols)

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        logging.exception("exception url %s",u)

def urllist_to_textgen_list(urls,chunk_size=int(32e6),encoding="utf8",
                            randomize=True):
    if randomize:
        urls=urls.copy()
        random.shuffle(urls)
    textgen_func=functools.partial(url_textgen,chunk_size=chunk_size,
                                   encoding=encoding)
    return map(textgen_func,urls)


#@bufgen_decorator
def urllist_textgen(urls,chunk_size=int(32e6),encoding="utf8"):
    iters=urllist_to_textgen_list(urls,chunk_size=chunk_size,
                                   encoding=encoding)
    return itertools.chain.from_iterable(iters)






def opus_mono_get_url(lang='fr',minsize=5e3):
    r=requests.get("http://opus.nlpl.eu/opusapi/",
                   params={"source":lang,
                                                  "version":"latest",
                                                  'preprocessing': 'mono'})
    d=r.json()
    urls=sorted(set( c['url']   for c in d['corpora'] \
            if  '.txt.gz' in c['url'] and int(c['size'])>minsize ))
    return urls


def opus_mono_textgen(lang='fr',encoding='utf8',chunk_size=int(8e6),minsize=5e3):
    urls=opus_mono_get_url(lang,minsize)
    return  urllist_textgen(urls,chunk_size,encoding)

