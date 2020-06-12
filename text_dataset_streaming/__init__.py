# -*- coding: utf-8 -*-
import logging
logging.getLogger('text_dataset_streaming').addHandler(logging.NullHandler())
logging.captureWarnings(True)
del logging


from .textfiles import urllist_textgen
from .wiki import wiki_article_generator
from .bufgen import threaded_bufgen,bufgen_decorator
from .opus import opus_mono_textgen

