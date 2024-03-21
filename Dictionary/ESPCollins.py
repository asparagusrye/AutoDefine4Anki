""" Because Collins use CloudFlare, which prevent the use headless browser for
    Anti"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
import re


class Word(object):
    """ retrive word info from collins spanish dictionary website """
    entry_selector = '.page > .dictionary'
    header_selector = '.top-container'

    title_selector = entry_selector + ' .title_container .orth'
    pronunciation_selector = entry_selector + " > .mini_h2"
    definition_body_selector = entry_selector + " .definitions > .hom"
    wordform_selector = " .gramGrp .pos"

    driver: webdriver = None

    @classmethod
    def get_url(cls, word):
        """ get url of word definition """
        baseurl = "https://www.collinsdictionary.com/dictionary/spanish-english/"
        return baseurl + word

    @classmethod
    def get(cls, word):
        """ get html soup of word """
        driver_options = webdriver.EdgeOptions()
        driver_options.add_argument('--blink-settings=imagesEnabled=false')
        # driver_options.add_experimental_option("detach", True)
        cls.driver = webdriver.Edge(options=driver_options)
        cls.driver.get(cls.get_url(word))

    @classmethod
    def name(cls):
        """ get word name """
        if cls.driver is None:
            return None
        return cls.driver.find_element(By.CSS_SELECTOR, cls.title_selector).text
    @classmethod
    def pronunciations(cls):
        """ get Lat Am and Spain pronunciations """
        if cls.driver is None:
            return None

        latam = {'prefix': None, 'mp3': None}
        spain = {'prefix': None, 'mp3': None}
        elements = cls.driver.find_element(By.CSS_SELECTOR, cls.pronunciation_selector).find_elements(By.XPATH, "./*")
        try:
            latam['mp3'] = elements[0].find_element(By.TAG_NAME, "a").get_attribute("data-src-mp3")
            latam['prefix'] = elements[1].text
            spain['mp3'] = elements[2].find_element(By.TAG_NAME, "a").get_attribute("data-src-mp3")
            spain['prefix'] = elements[3].text
        except IndexError:
            pass
        return [latam, spain]

    @classmethod
    def definitions(cls):
        word_infos = []
        namespaces = cls.driver.find_elements(By.CSS_SELECTOR, cls.definition_body_selector)
        for namespace in namespaces:
            word_info = {}
            try:
                wordform = namespace.find_element(By.CSS_SELECTOR, cls.wordform_selector).text
            except:
                #in the definition there is no p.o.s information of this word
                # e.j. a la orden
                wordform = "__GLOBAL__"
            # use the wordform i.e. the p.o.s of the word as the namespace
            word_info["namespace"] = wordform
            word_info["definitions"] = []
            definitions = namespace.find_elements(By.CSS_SELECTOR, " .gramGrp > .sense")
            if not len(definitions):
                # in this case the .sense lie immediately under '.hom' not under .gramGrp
                definitions = namespace.find_elements(By.CSS_SELECTOR, ".hom > .sense")
            for definition in definitions:
                word_definition = {}
                description = ""
                description_examples = []
                for tag in definition.find_elements(By.XPATH, "./*"):
                    classes = tag.get_attribute("class")
                    # try to get the word definition (description)
                    if re.search(r'\btype-syn\b', classes) or re.search(r'\bgramGrp\b', classes) or re.search(r'\btype-subj\b', classes) or re.search(
                            r'\btype-translation\b', classes) or re.search(r'\bsense\b', classes) and not re.search(
                            r'\bxr\b', classes):
                        description += tag.text + "\n"

                    # try to get the examples for that definition (description)
                    if "type-example" in tag.get_attribute("class"):
                        quote = tag.find_element(By.CSS_SELECTOR, ".type-example > .quote").text
                        translation = tag.find_element(By.CSS_SELECTOR, ".type-example >.type-translation").text
                        description_examples.append({"quote": quote, "translation": translation})

                    if "type-phr" in tag.get_attribute("class"):
                        quote = tag.find_element(By.CSS_SELECTOR, ".type-phr > .type-phr").text
                        translation = ""
                        try:
                            translation = tag.find_element(By.CSS_SELECTOR, ".type-phr > .type-translation").text
                        except:
                            pass
                        subdefintion = {"quote": quote, "translation": translation, "examples": []}
                        subsexamples = tag.find_elements(By.CSS_SELECTOR, ".type-phr > .type-example")
                        for subexample in subsexamples:
                            subquote = tag.find_element(By.CSS_SELECTOR, ".type-example > .quote").text
                            subtranslation = tag.find_element(By.CSS_SELECTOR,
                                                              ".type-example >.type-translation").text
                            subdefintion["examples"].append({"quote": subquote, "translation": subtranslation})

                        description_examples.append(subdefintion)

                word_definition['description'] = description
                word_definition['examples'] = description_examples
                word_info['definitions'].append(word_definition)
            word_infos.append(word_info)

        # pretty = json.dumps(word_infos, indent=4)
        # print(pretty)
        print(word_infos)


if __name__ == '__main__':
    Word.get("negar")
    Word.definitions()