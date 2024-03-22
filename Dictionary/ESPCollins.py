""" Because Collins use CloudFlare, which prevents the use headless browser for
    scrapping. For Collins Dictionaries, selenium (headfull broswer) is used"""
import traceback
from typing import List

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from WordNotFound import WordNotFound
import stanza


class Word:
    """ retrieve word info from collins spanish dictionary website """
    word_entry: webdriver = None
    nlp = stanza.Pipeline(lang="es", processors='tokenize,mwt,pos,lemma',
                          download_method=stanza.DownloadMethod.REUSE_RESOURCES)

    entry_selector = '.page > .dictionaries > .dictionary'
    header_selector = '.top-container'

    title_selector = '.title_container .orth'
    pronunciation_selector = ".mini_h2"
    definition_body_selector = ".definitions > .hom"
    pos_selector = ".gramGrp .pos"

    @classmethod
    def get_url(cls, key_word):
        # get url of word definition
        baseurl = "https://www.collinsdictionary.com/dictionary/spanish-english/"
        return baseurl + key_word

    @classmethod
    def get(cls, key_word):
        # get the web driver, go to the url of the word
        driver_options = webdriver.EdgeOptions()
        driver_options.add_argument('--blink-settings=imagesEnabled=false')
        # driver_options.add_experimental_option("detach", True)
        browser = webdriver.Edge(options=driver_options)
        browser.get(cls.get_url(key_word))
        dictionaries = browser.find_elements(By.CSS_SELECTOR, cls.entry_selector)
        if len(dictionaries) == 0:
            raise WordNotFound()
        cls.word_entry = dictionaries[0] if len(dictionaries) == 1 else dictionaries[1]

    @classmethod
    def name(cls):
        # get word name
        if cls.word_entry is None:
            return None
        return cls.word_entry.find_element(By.CSS_SELECTOR, cls.title_selector).text

    @classmethod
    def pronunciations(cls):
        # get Lat Am and Spain pronunciations

        if cls.word_entry is None:
            return None

        latam = {'prefix': None, 'mp3': None}
        spain = {'prefix': None, 'mp3': None}
        elements = cls.word_entry.find_element(By.CSS_SELECTOR, cls.pronunciation_selector).find_elements(By.XPATH,
                                                                                                          "./*")
        try:
            latam['mp3'] = elements[0].find_element(By.TAG_NAME, "a").get_attribute("data-src-mp3")
            latam['prefix'] = elements[1].text
            spain['mp3'] = elements[2].find_element(By.TAG_NAME, "a").get_attribute("data-src-mp3")
            spain['prefix'] = elements[3].text
        except IndexError:
            print("There was an error with indexing while reading pronunciation tags")
        except Exception as e:
            print(traceback.print_exc())
        return [latam, spain]

    @classmethod
    def definitions(cls):
        word_definitions = []

        # Some words can be both feminine and masculine nouns. In the dictionary, the definition of the word
        # will be divided into several sections based on its part of speech. Therefore, we will use
        # the part of speech as the namespace of the word info.
        namespaces = cls.word_entry.find_elements(By.CSS_SELECTOR, cls.definition_body_selector)

        for namespace in namespaces:
            info_in_namespace = {}
            try:
                pos = namespace.find_element(By.CSS_SELECTOR, cls.pos_selector).text
            except selenium.common.exceptions.NoSuchElementException:
                # in the dictionary, some words don't have p.o.s. In this case, we'll name the namespace __GlOBAl__
                pos = "__GLOBAL__"
            # use the the p.o.s of the word as the namespace
            info_in_namespace["namespace"] = pos

            info_in_namespace["definitions"] = []

            senses_under_gramgrp = namespace.find_elements(By.CSS_SELECTOR, " .gramGrp > .sense")
            # in this case the .sense lie immediately under '.hom' not under .gramGrp
            senses = senses_under_gramgrp if len(senses_under_gramgrp) != 0 else namespace.find_elements(
                By.CSS_SELECTOR, ".hom > .sense")

            for sense in senses:
                definition_info = {}
                definition = ""
                examples = []

                for sense_element in sense.find_elements(By.XPATH, "./*"):
                    element_classes = sense_element.get_attribute("class").split(" ")
                    # try to get the word definition (description)
                    if any(element_class in element_classes for element_class in
                           ['type-syn', 'gramGrp', 'type-subj', 'type-translation',
                            'sense']) and 'xr' not in element_classes:
                        definition += sense_element.text + "\n"

                    # try to get the examples for that definition (description)
                    if "type-example" in element_classes:
                        quote = sense_element.find_element(By.CSS_SELECTOR, ".type-example > .quote").text
                        translation = sense_element.find_element(By.CSS_SELECTOR,
                                                                 ".type-example >.type-translation").text
                        examples.append({"quote": quote, "translation": translation})

                    if "type-phr" in element_classes:
                        quote = sense_element.find_element(By.CSS_SELECTOR, ".type-phr > .type-phr").text
                        translation = ""
                        try:
                            translation = sense_element.find_element(By.CSS_SELECTOR,
                                                                     ".type-phr > .type-translation").text
                        except:
                            pass

                        subdefintion = {"quote": quote, "translation": translation, "examples": []}
                        subsexamples = sense_element.find_elements(By.CSS_SELECTOR, ".type-phr > .type-example")
                        for subexample in subsexamples:
                            subquote = sense_element.find_element(By.CSS_SELECTOR, ".type-example > .quote").text
                            subtranslation = sense_element.find_element(By.CSS_SELECTOR,
                                                                        ".type-example >.type-translation").text
                            subdefintion["examples"].append({"quote": subquote, "translation": subtranslation})

                        examples.append(subdefintion)

                definition_info['definition'] = definition
                definition_info['examples'] = examples
                info_in_namespace['definitions'].append(definition_info)
            word_definitions.append(info_in_namespace)
        # print(word_definitions)
        return word_definitions

    @classmethod
    def info(cls, replace_keyword=True):
        word_info = {
            "name": cls.name(),
            "pronunciations": cls.pronunciations(),
            "definitions": cls.definitions()
        }
        word_info["definitions_in_html"] = cls.definitions_in_html(word_info["name"], word_info["definitions"],
                                                                   replace_keyword)
        return word_info

    @classmethod
    def definitions_in_html(cls, key_word, definitions, replace_keyword=True, replacement="____"):
        def bold(string):
            return f'<b>{string}</b>'

        def italic(string):
            return f'<i>{string}</b>'

        def list_item(string):
            return f'<li>{string}</li>'

        def make_unordered_list(strings: List[str]) -> str:
            return f'<ul>{"\n".join([string for string in strings])}</ul>'

        def make_ordered_list(strings: List[str]) -> str:
            return f'<ol>{"\n".join([string for string in strings])}</ol>'

        definitions_in_html = definitions
        for namespace in definitions_in_html:
            for definition_in_namespace in namespace["definitions"]:
                definition_in_namespace["definition"] = bold(definition_in_namespace["definition"])
                list_of_examples = []
                for example in definition_in_namespace["examples"]:
                    if replace_keyword:
                        words_to_replace = [key_word]
                        doc = cls.nlp(example["quote"])
                        for sentences in doc.sentences:
                            for word in sentences.words:
                                if word.lemma == key_word:
                                    words_to_replace.append(word.text)
                        words_to_replace = sorted(list(set(words_to_replace)), key=len)
                        for word_to_replace in words_to_replace:
                            example["quote"] = example["quote"].replace(word_to_replace, replacement)
                    example["quote"] = italic(example["quote"])
                    example["translation"] = bold(example["translation"])
                    list_of_examples.append(list_item(f'{example["quote"]}: {example["translation"]}'))
                make_ordered_list(list_of_examples)

        print(definitions_in_html)
        return definitions


if __name__ == '__main__':
    Word.get("poner")
    Word.info()
    list_of_lemmas = ['final', 'final', 'finales', 'final']
