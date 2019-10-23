# -*- coding: utf-8 -*-

import pypandoc


import mediawiki_parser
import mediawiki_parser.preprocessor, mediawiki_parser.text

from mwxml import Dump
import smart_open




def wikiparse(text):
    templates = {}


    preprocessor = mediawiki_parser.preprocessor.make_parser(templates)

    parser =  mediawiki_parser.text.make_parser()

    preprocessed_text = preprocessor.parse(text)
    output = parser.parse(preprocessed_text)
    return output.leaves()


def wiki_article_generator(source,len_threshold=50):
        with smart_open.open(source) as f:

            dump = Dump.from_file(f)
            for page in dump.pages:
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
                    yield (page.title,text)