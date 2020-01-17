# -*- coding: utf-8 -*-
import requests
import xml.parsers.expat
import threading
import queue
import random
import smart_open


from .textfiles import urllist_textgen



def opus_mono_get_url(lang='fr',minsize=5e3):
    r=requests.get("http://opus.nlpl.eu/opusapi/",
                   params={"source":lang,
                                                  "version":"latest",
                                                  'preprocessing': 'mono'})
    d=r.json()
    urls=sorted(set( c['url']   for c in d['corpora'] \
            if  '.txt.gz' in c['url'] and int(c['size'])>minsize ))
    return urls


def opus_mono_textgen(lang='fr',encoding='utf8',chunk_size=int(8e6),minsize=5e3,
                      randomize=True):
    urls=opus_mono_get_url(lang,minsize)
    return  urllist_textgen(urls,chunk_size,encoding,randomize=randomize)


def build_pair_dataset_url_list(source_lang="fr",target_lang="en"):
  source_lang="fr"
  target_lang="en"
  r=requests.get("http://opus.nlpl.eu/opusapi/",params={"source":source_lang,"version":"latest","target":target_lang})
  d=r.json()
  url_tmx=sorted(set( c['url']   for c in d['corpora'] if c['preprocessing']=='tmx'   ))
  random.shuffle(url_tmx)
  return url_tmx
# return pairgen(url_tmx)
def pair_dataset_gen(source_lang="fr",target_lang="en",minsize_text=0,maxsize_text=0):
  url_tmx= build_pair_dataset_url_list(source_lang="fr",target_lang="en")
  return pairgen(url_tmx,source_lang=source_lang,target_lang=target_lang,
                 minsize_text=minsize_text,maxsize_text=maxsize_text)



def queue_pairs(url,pair_queue,source_lang="fr",target_lang="en",minsize_text=0):

  f=smart_open.open(url,mode="rb")
  # 3 handler functions





  parse_state={"curtag":"","lang":"",
               "record":{source_lang:"",target_lang:""}.copy()}.copy()
  def start_element(name, attrs):

      if 'xml:lang' in attrs:
        parse_state ["lang"]=attrs['xml:lang']
      parse_state ["curtag"]=name
      if name=="tu":
        parse_state ["record"]={source_lang:"",target_lang:""}.copy()



  def end_element(name):

      record=parse_state ["record"]
      if name=="tu":
        p=(record[source_lang],record[target_lang])
        if minsize_text==0 or all(len(s)>minsize_text for s in p):

          pair_queue.put(p)

  def char_data(data):
    record=parse_state ["record"]
    if parse_state ["curtag"]=="seg":
      lang=parse_state ["lang"]
      t=record.get(lang,"")
      t+=data
      record[lang]=t.strip()






  p = xml.parsers.expat.ParserCreate()

  p.StartElementHandler = start_element
  p.EndElementHandler = end_element
  p.CharacterDataHandler = char_data

  p.ParseFile(f)
def pairgen(urls,maxsize=3,source_lang="fr",target_lang="en",minsize_text=0,maxsize_text=0):
    """
        queue buffer of maxsize of gen iterator
    """
    lock = threading.Lock()
    q=queue.Queue(maxsize=2)
    for url in urls:






      task=threading.Thread(target=queue_pairs,
                            args=(url,q,source_lang,target_lang,minsize_text)
                             )
      task.start()


      while task.is_alive():
        with lock:
          try:
            p=q.get(timeout=1)
            if maxsize_text==0 or all(len(s)<maxsize_text for s in p):
              yield p
          except queue.Empty:
              pass
