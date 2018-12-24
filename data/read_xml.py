import time
import os
import codecs
import csv
import xml.etree.ElementTree as etree
import re

import mwparserfromhell

from data.config import WIKIPEDIA_XML, WIKIPEDIA_WORKING_DIR, WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE
from data.read_write_txt import FilesReaderBinaryUTF8, FilesWriterBinaryUTF8


def mwparserfromhell_remove_templates(text):
    """
    Removes templates from wikicode parsed tree.
    Note: I'm not even sure what this does or if it does something.
    """
    wikicode = mwparserfromhell.parse(text)
    for template in reversed(wikicode.filter_templates()):
        wikicode.remove(template)
    return wikicode


def wikicode_to_txt(wikicode):
    """
    I couldn't find a properly-licensed tool to do this, I created my own.
    This mostly crushes wikicode to plain text, but it's not perfect.
    """
    # removes wiki markup: https://en.wikipedia.org/wiki/Wikipedia:Tutorial/Formatting#Wiki_markup
    
    # matches everything but a `<`, a `}`, or a `}`.
    everything_but_closing_parenthesis = '[^\]\<\}]'
    
    # matches a `[`, a `{`, or a `<ref>`:
    begin = '(\{|\[|\<ref\>)+'
    # matches anywhing and then a final `:` or a final `|`:
    preceded = '(' + everything_but_closing_parenthesis + '+(\||:))?'
    
    # matches a `]`, a `}`, or a `</ref>.:
    closing = '(\]|\}|\</ref\>)+'

    # matches the last thing between "begin" and "closing" which is preceded by "preceded".:
    RE = begin + preceded + '(?P<text>' + everything_but_closing_parenthesis + '*)' + closing
    RE = re.compile(RE)

    # Keep the "<text>" group found before closing parenthesis.
    keep_right_group = r'\g<text>'

    out = re.sub(RE, keep_right_group, wikicode)
    
    # remove remaining refs and xml comments.
    RE = "((</?ref)[^\>]*\>|(<!--)[^\>]*--\>)"
    out = re.sub(RE, "", out)
    
    # remove a whole lot of crap
    out = out.replace("'''", "").replace("''", "").replace("  ", " ").replace("--", "").replace("~~", "").replace("\t", " ").replace("  ", " ")
    out = out.replace("\n*", "\n").replace("\n#", "\n").replace(" \n", "\n").replace("\n ", "\n").replace(" \n", "\n")
    out = out.replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n")
    
    return out


def beautify_text_to_sentences_that_ends_with_dots(text): 
    """
    Make sentences end with dots whenever possible or where there is a dot missing.
    """
    symbols_to_avoid = ["^", "\n", "\.", "\!", ",", "-", ":", ";", "\?"]
    not_an_empty_nor_starting_nor_punctuated_line = ""
    for symb in symbols_to_avoid:
        not_an_empty_nor_starting_nor_punctuated_line += '(?<!' + symb + ')'
    #not_an_empty_nor_starting_nor_punctuated_line = "(?<!^)(?<!\n)"
    RE = not_an_empty_nor_starting_nor_punctuated_line + "(?P<eos>(\n|$))"
    RE = re.compile(RE)

    # Keep the "<text>" group found before closing parenthesis.
    keep = r'.\g<eos>'

    out = re.sub(RE, keep, text)
    
    return out


def remove_titles_and_insert_newline_instead(text):
    """
    A title will now be 2 new lines, and an article separation will now be 3 newlines.
    """
    RE = re.compile("(((?<=^)|(?<=\n)))((=|_).*(=|_)\s?\.?\s?)(\n|$)")
    out = re.sub(RE, "\n", text)
    out = out.strip().rstrip("\n") + "\n\n\n"
    return out

def title_tag_name_to_clean_title(title_tag):
    i = title_tag.rfind("}")
    if i != -1:
        return title_tag[i + 1:]
    else: 
        return title_tag



    
def convert_wikipedia_to_plain_txt(WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE, WIKIPEDIA_XML):
    # With a writer on text files
    with FilesWriterBinaryUTF8(WIKIPEDIA_OUTPUT_UTF8_TXT_RAW_FILE, chunk_size=int(1024**2), verbose=True) as fswr:

        title = ""
        # For every note in Wikipedia's XML dump
        for event, elem in etree.iterparse(WIKIPEDIA_XML, events=('start', 'end')):

            tname = title_tag_name_to_clean_title(elem.tag)

            # Retrieve pages just under certain conditions.
            if event == 'start':
                if tname == 'title':
                    title = elem.text
                elif (
                    tname == 'text'
                    # Discard if no title or no text:
                    and elem.text is not None 
                    and title is not None 
                    # Discard if page is a redirection to another page:
                    and "{{redirect" not in elem.text.lower()
                    and "#redirect" not in elem.text.lower()
                    # Discard if the page is not a regular article (ex type: page, list, talk, book):
                    and ":" not in title
                ):  

                    # Will save this page. 

                    text = elem.text

                    wikicode = mwparserfromhell_remove_templates(text)
                    text = wikicode_to_txt(str(wikicode))
                    text = beautify_text_to_sentences_that_ends_with_dots(text)
                    text = remove_titles_and_insert_newline_instead(text)

                    fswr.write(text)

                elem.clear()

