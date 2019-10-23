# -*- coding: utf-8 -*-
import requests
import smart_open
import random
import logging

def urllist_textgen(urls,chunk_size=int(32e6),encoding="utf8"):
    for u in urls:
        try:
            with smart_open.open(u,mode="rt",
                     encoding=encoding,errors="ignore") as f:
              t=f.read(chunk_size)
              while len(t)>0:
                yield t
                t=f.read(chunk_size)
        except:
            logging.exception("eception url %s",u)

def opus_mono_textgen(lang='fr',encoding='utf8',chunk_size=int(32e6),minsize=5e3):
    r=requests.get("http://opus.nlpl.eu/opusapi/",params={"source":lang,"version":"latest", 'preprocessing': 'mono'})
    d=r.json()
    urls=sorted(set( c['url']   for c in d['corpora'] \
            if  '.txt.gz' in c['url'] and int(c['size'])>minsize ))
    random.shuffle(urls)
    return  urllist_textgen(urls,chunk_size,encoding)
