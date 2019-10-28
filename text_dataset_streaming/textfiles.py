# -*- coding: utf-8 -*-
import requests
import smart_open
# -*- coding: utf-8 -*-

import random
import logging
import functools
import itertools
from .bufgen import threaded_bufgen,bufgen_decorator

def split_ligne(t,chunk_size=int(32e6)):
    lreste=chunk_size-len(t)
    lreste=int(lreste)
    if lreste<0:
        return t,""
    else:
        texte=""
        l=t[4096:].rsplit("\n",1)
        if len(l)>1:
              texte1,reste=l
        else:
              texte=l[0]
              reste=""
        texte=t[:4096]+texte
        if len(reste)>0 and reste[-1]=="\n":
            texte+=reste
            reste=""
        return texte,reste

@bufgen_decorator
def url_textgen(u,chunk_size=int(32e6),encoding="utf8"):
    reste=""
    try:
        with smart_open.open(u,
                 encoding=encoding,errors="ignore") as f:
          t=f.read(chunk_size)
          texte,reste=split_ligne(t,chunk_size*0.8)
          while len(t)>0:
            yield texte
            t=f.read(chunk_size)
            texte,reste=split_ligne(reste+t,chunk_size*0.8)
        if len(reste)>0:
            yield reste

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        logging.exception("exception url %s",u)

def urllist_to_textgen_list(urls,chunk_size=int(32e6),encoding="utf8"):
    textgen_func=functools.partial(url_textgen,chunk_size=chunk_size,
                                   encoding=encoding)
    return map(textgen_func,urls)

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

