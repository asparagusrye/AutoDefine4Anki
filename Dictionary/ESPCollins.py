""" Because Collins use CloudFlare, which prevents the use headless browser for
    scrapping. For Collins Dictionaries, selenium (headfull broswer) is used"""
import traceback
from typing import Dict

from bs4 import BeautifulSoup
import selenium.common.exceptions
from selenium import webdriver
from .WordNotFound import WordNotFound
from .TextFormatingHTML import *
import spacy


class Word:
    """ retrieve word info from collins spanish dictionary website """
    word_entry: webdriver = None

    nlp = spacy.load("es_dep_news_trf")

    entry_selector = '.page > .dictionaries > .dictionary'
    header_selector = '.top-container'

    title_selector = '.title_container .orth'
    pronunciation_selector = ".mini_h2"
    definition_body_selector = ".definitions > .hom"
    pos_selector = ".gramGrp .pos"

    skip_class_list = ["sensenum", "xr"]
    space_after_class_list = ['type-syn', 'type-register', 'rend-b']
    newline_after_class_list = ['gramGrp', 'type-subj', 'type-translation',
                                'sense']

    global_namespace = "__GLOBAL__"

    @classmethod
    def get_url(cls, key_word: str) -> str:
        # get url of word definition
        baseurl = "https://www.collinsdictionary.com/dictionary/spanish-english/"
        return baseurl + key_word

    @classmethod
    def get(cls, key_word: str) -> None:
        # get the web driver, go to the url of the word
        driver_options = webdriver.EdgeOptions()
        driver_options.add_argument('--blink-settings=imagesEnabled=false')
        # driver_options.add_experimental_option("detach", True)
        driver = webdriver.Edge(options=driver_options)
        driver.get(cls.get_url(key_word))
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        dictionaries = soup.select(cls.entry_selector)
        if len(dictionaries) == 0:
            raise WordNotFound()
        cls.word_entry = dictionaries[0] if len(dictionaries) == 1 else dictionaries[1]

    @classmethod
    def name(cls) -> str:
        # get word name
        if cls.word_entry is None:
            return None
        return cls.word_entry.select_one(cls.title_selector).get_text(strip=True)

    @classmethod
    def pronunciations(cls) -> dict[str, str] | None:
        # get Lat Am and Spain pronunciations

        if cls.word_entry is None:
            return None

        pronunciations_url = {}
        elements = cls.word_entry.select_one(cls.pronunciation_selector).find_all(recursive=False)
        try:
            pronunciations_url[elements[1].get_text(strip=True)] = elements[0].select_one("a").attrs["data-src-mp3"]
            pronunciations_url[elements[3].get_text(strip=True)] = elements[2].select_one("a").attrs["data-src-mp3"]
        except IndexError:
            print("There was an error with indexing while reading pronunciation tags")
        except Exception as e:
            print(traceback.print_exc())
        return pronunciations_url

    @classmethod
    def definitions(cls) -> List:
        def contain_class(classes_to_search: List[str], element_classes: List[str]) -> bool:
            return any(element_class in element_classes for element_class in classes_to_search)

        word_definitions = []

        # Some words can be both feminine and masculine nouns. In the dictionary, the definition of the word
        # will be divided into several sections based on its part of speech. Therefore, we will use
        # the part of speech as the namespace of the word info.
        namespaces = cls.word_entry.select(cls.definition_body_selector)

        for namespace in namespaces:
            info_in_namespace = {}
            try:
                pos = namespace.select_one(cls.pos_selector).get_text(strip=True)
            except selenium.common.exceptions.NoSuchElementException:
                # in the dictionary, some words don't have p.o.s. In this case, we'll name the namespace __GlOBAl__
                pos = cls.global_namespace
            # use the the p.o.s of the word as the namespace
            info_in_namespace["namespace"] = pos
            info_in_namespace["definitions"] = []

            senses_under_gramgrp = namespace.select(" .gramGrp > .sense")
            # in this case the .sense lie immediately under '.hom' not under .gramGrp
            senses = senses_under_gramgrp if len(senses_under_gramgrp) != 0 else namespace.select(".hom > .sense")

            for sense in senses:
                definition_info = {}
                definition = ""
                examples = []

                for sense_element in sense.find_all(recursive=False):
                    element_classes = sense_element.attrs["class"]
                    # skip sense numbering at the beginning of the definition
                    if contain_class(cls.skip_class_list, element_classes):
                        continue
                    # try to get the word definition (description)
                    if contain_class(cls.newline_after_class_list, element_classes):
                        definition += sense_element.get_text(strip=True) + "\n"

                    if contain_class(cls.space_after_class_list, element_classes):
                        definition += sense_element.get_text(strip=True) + " "

                    if "punctuation" in element_classes:
                        if definition[-1] == "\n":
                            definition = definition[:-1]
                        if sense_element.text == "(":
                            definition += " ("
                        else:
                            definition += ") "

                    if 'bluebold' in element_classes:
                        definition = definition[:-1]
                        definition += f" {sense_element.get_text(strip=True)} "
                    # try to get the examples for that definition (description)
                    if "type-example" in element_classes:
                        quote = sense_element.select_one(".type-example > .quote").get_text(strip=True)
                        translation = sense_element.select_one(".type-example >.type-translation").get_text(strip=True)
                        examples.append({"quote": quote, "translation": translation})

                    if contain_class(["type-phr", "type-idm"], element_classes):
                        element_class = "type-phr" if "type-phr" in element_classes else "type-idm"
                        quote = sense_element.select_one(f".{element_class} > .orth").get_text(strip=True)
                        if type_syn := sense_element.select_one(f".{element_class} > .type-syn"):
                            quote += " " + type_syn.get_text(strip=True)
                        translation = ""
                        if element := sense_element.select_one(f".{element_class} > .type-translation"):
                            translation = element.get_text(strip=True)
                        subdefintion = {"quote": quote, "translation": translation, "examples": []}
                        subexamples = sense_element.select(f".{element_class} > .type-example")
                        for subexample in subexamples:
                            subquote = subexample.select_one(".quote").get_text(strip=True)
                            subtranslation = subexample.select_one(".type-translation").get_text(
                                strip=True)
                            subdefintion["examples"].append({"quote": subquote, "translation": subtranslation})
                        examples.append(subdefintion)

                definition_info['definition'] = definition.strip(" \n")
                definition_info['examples'] = examples
                info_in_namespace['definitions'].append(definition_info)
            word_definitions.append(info_in_namespace)
        return word_definitions

    @classmethod
    def info(cls, replace_keyword: bool = True) -> Dict:
        word_info = {
            "name": cls.name(),
            "pronunciations": cls.pronunciations(),
            "definitions": cls.definitions()
        }
        word_info["definitions_in_html"] = cls.definitions_in_html(word_info["name"], word_info["definitions"],
                                                                   replace_keyword)
        return word_info

    @classmethod
    def replace_word(cls, key_word: str, sentence: str, replacement: str = "____") -> str:
        words_to_replace = []
        for token in cls.nlp(sentence):
            if token.lemma_ == key_word:
                words_to_replace.append(token.text)
        words_to_replace = sorted(list(set(words_to_replace)), key=len, reverse=True)
        for word_to_replace in words_to_replace:
            sentence = sentence.replace(word_to_replace, replacement)
        return sentence

    @classmethod
    def definitions_in_html(cls, key_word, definitions, replace_keyword=True):
        html_content = []
        for namespace in definitions:
            html_namespace = ""
            if namespace["namespace"] != cls.global_namespace:
                html_namespace += div(italic(namespace["namespace"].upper()))

            html_definitions = []
            for definition_in_namespace in namespace["definitions"]:
                # html_namespace_content += list_item(bold(definition_in_namespace["definition"]))
                html_definitions.append(list_item(bold(definition_in_namespace["definition"])))
                html_examples = []
                for example in definition_in_namespace["examples"]:
                    quote = cls.replace_word(key_word, example["quote"]) if replace_keyword else example["quote"]
                    quote_html = bold(quote)
                    translation_html = italic(example["translation"])
                    html_examples.append(list_item(f"{quote_html}: {translation_html}"))

                    if "examples" in example:
                        html_subexamples = []
                        for subexample in example["examples"]:
                            subquote = cls.replace_word(key_word, subexample["quote"]) if replace_keyword else \
                                subexample[
                                    "quote"]
                            subquote_html = bold(subquote)
                            subtranslation_html = italic(subexample["translation"])
                            html_subexamples.append(list_item(f"{subquote_html}: {subtranslation_html}"))
                        html_examples.append(make_unordered_list(html_subexamples))
                html_definitions.append(make_unordered_list(html_examples))
            html_content.append(html_namespace + make_ordered_list(html_definitions))
        return str(BeautifulSoup("<hr>".join(html_content), "html.parser"))


if __name__ == '__main__':
    Word.get("final")
    word = Word.info()
    print(word)
