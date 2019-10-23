from text_dataset_streaming import urllist_textgen,opus_mono_textgen
from text_dataset_streaming import wiki_article_generator



def test_opus():
    gen=opus_mono_textgen(encoding='utf8',chunk_size=16000)
    text=next(gen)

    assert abs(len(text)-16000)<300



