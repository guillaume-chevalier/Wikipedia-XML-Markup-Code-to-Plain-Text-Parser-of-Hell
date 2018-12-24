
# coding: utf-8

# # Wikipedia XML Markup Code to Plain Text Parser
# 
# > Dumping wikipedia to splitted txt files.
# 
# Installation infos and how it works: 
# 1. Edit `./data/config.py` to locate your article `.xml` wikipedia file extracted from the `.bz2` compressed file. This XML could weight as much as 60 GB. There might be a way to dynamically unzip it from within python without extracting it first, but here the XML is the starting point. In `./data/config.py`, also add your other paths for where you will want to save the txt dump files.
# 2. Run `main.py` (which is the same code as in the readme/notebook) to launch the conversion.
# 3. Later, you will be able to read the txt files from disk with the following class: `from data.read_write_txt import FilesReaderBinaryUTF8`. See an example usage commented at the bottom. 
# 

# In[1]:


# get_ipython().system('cat requirements.txt')


# In[2]:


import os

from data.config import WIKIPEDIA_XML, WIKIPEDIA_WORKING_DIR, WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE
from data.read_write_txt import FilesReaderBinaryUTF8
from data.read_xml import wikicode_to_txt,     beautify_text_to_sentences_that_ends_with_dots, convert_wikipedia_to_plain_txt


# In[3]:


if not os.path.exists(WIKIPEDIA_WORKING_DIR):
    os.mkdir(WIKIPEDIA_WORKING_DIR)

print("WIKIPEDIA_XML:", WIKIPEDIA_XML)
print("WIKIPEDIA_WORKING_DIR:", WIKIPEDIA_WORKING_DIR)
print("WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE:", WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE)


# In[4]:


def test_can_remove_wikicode_to_clean():
    before = "<!-- heyyyo-->{cat:t|test1}, ''' ''<ref>[[catt|test2]]</ref>''' '',[[}} [[catt:test3]] [{test}]~<ref name=lloolol></ref>.--~~~~"
    expected = "test1, test2 , test3 test~."

    result = wikicode_to_txt(before)

    assert (result == expected)

def test_can_remove_refs_and_code_quotes():
    before = "the Latin ''trealala''...<ref name=werr /><ref name=nyt1></ref><ref></ref>"
    expected = "the Latin trealala..."

    result = wikicode_to_txt(before)

    assert (result == expected)

def test_can_end_sentences_cleanly():
    before = "\neeer\ntest.\ntestr.\ntest!\n\ntest2"
    expected = "\neeer.\ntest.\ntestr.\ntest!\n\ntest2."

    result = beautify_text_to_sentences_that_ends_with_dots(before)

    assert (result == expected)

test_can_remove_wikicode_to_clean()
test_can_remove_refs_and_code_quotes()
test_can_end_sentences_cleanly()


# In[5]:


if __name__ == "__main__": 
    convert_wikipedia_to_plain_txt(WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE, WIKIPEDIA_XML)
    # # Test:
    # with FilesReaderBinaryUTF8(WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE, verbose=True) as f:
    #     print(f.next_paragraph())


# ## License
# 
# BSD 3-Clause License
# 
# 
# Copyright (c) 2018, Guillaume Chevalier
# 
# All rights reserved.
# 
