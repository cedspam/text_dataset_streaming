# -*- coding: utf-8 -*-
import re
import pypandoc


import mediawiki_parser
import mediawiki_parser.preprocessor, mediawiki_parser.text

from mwxml import Dump
import smart_open


wikimedia_fr_url=["https://dumps.wikimedia.freemirror.org/frwikisource/latest/frwikisource-latest-pages-articles-multistream.xml.bz2",
          "https://dumps.wikimedia.freemirror.org/frwiki/latest/frwiki-latest-pages-articles-multistream.xml.bz2",
         "https://dumps.wikimedia.freemirror.org/frwikiversity/latest/frwikiversity-latest-pages-articles.xml.bz2",
         "https://dumps.wikimedia.freemirror.org/frwikibooks/latest/frwikibooks-latest-pages-articles.xml.bz2",
         "https://dumps.wikimedia.freemirror.org/frwikivoyage/latest/frwikivoyage-latest-pages-articles.xml.bz2",
         "https://dumps.wikimedia.your.org/frwikiversity/latest/frwikiversity-latest-pages-articles-multistream.xml.bz2",
         "https://dumps.wikimedia.your.org/frwikibooks/latest/frwikibooks-latest-pages-articles-multistream.xml.bz2",
        "https://dumps.wikimedia.your.org/frwikiquote/latest/frwikiquote-latest-pages-articles-multistream.xml.bz2",
         "https://dumps.wikimedia.your.org/frwiki/latest/frwiki-latest-pages-articles-multistream.xml.bz2"
        


         
        
        ]


def wikiparse(text):
    templates = {}


    preprocessor = mediawiki_parser.preprocessor.make_parser(templates)

    parser =  mediawiki_parser.text.make_parser()

    preprocessed_text = preprocessor.parse(text)
    output = parser.parse(preprocessed_text)
    return output.leaves()


def wiki_article_generator(source,len_threshold=50,namespace=0):
        with smart_open.open(source) as f:

            dump = Dump.from_file(f)
            for page in dump.pages:
                if namespace is  None or page.namespace==namespace:
                    # Iterate through a page's revisions
                    for revision in page:
                        pass

                    text=revision.text
                    if text is not None and len(text)>len_threshold:

                        text=text.strip()

                        if  any( t in page.title   for t in [".djvu",".jpg",".png"]):
                            continue
                        title=page.title.replace("/"," - ")
                        title=title.replace("\\"," - ")

                        try:
                            text=pypandoc.convert_text(text,'plain','mediawiki')

                        except:
                            try:
                                text=wikiparse(text)
                            except:
                                pass
                    #nettoyage restant
                    text=re.sub(r"\[\d*?\]","",text).replace("{{,}}","")
                    text="\n".join(s.rstrip() for s in text.split("\n") if s.strip()!="")
                    text=re.sub(r"\n[ .,]*\n","",text)
                    
                    yield (page.title,text)
