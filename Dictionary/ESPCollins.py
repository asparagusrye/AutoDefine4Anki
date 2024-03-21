""" Because Collins use CloudFlare, which prevents the use headless browser for
    scrapping. For Collins Dictionaries, selenium (headfull broswer) is used"""
import traceback

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By


class Word:
    """ retrieve word info from collins spanish dictionary website """
    driver = None

    entry_selector = '.page > .dictionary'
    header_selector = '.top-container'

    title_selector = entry_selector + ' .title_container .orth'
    pronunciation_selector = entry_selector + " > .mini_h2"
    definition_body_selector = entry_selector + " .definitions > .hom"
    pos_selector = " .gramGrp .pos"

    @classmethod
    def get_url(cls, word):
        # get url of word definition
        baseurl = "https://www.collinsdictionary.com/dictionary/spanish-english/"
        return baseurl + word

    @classmethod
    def get(cls, word):
        # get the web driver, go to the url of the word
        driver_options = webdriver.EdgeOptions()
        driver_options.add_argument('--blink-settings=imagesEnabled=false')
        # driver_options.add_experimental_option("detach", True)
        cls.driver = webdriver.Edge(options=driver_options)
        cls.driver.get(cls.get_url(word))

    @classmethod
    def name(cls):
        # get word name
        if cls.driver is None:
            return None
        return cls.driver.find_element(By.CSS_SELECTOR, cls.title_selector).text

    @classmethod
    def pronunciations(cls):
        # get Lat Am and Spain pronunciations

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
            print("There was an error with indexing while reading pronunciation tags")
        except Exception as e:
            print(traceback.print_exc())
        return [latam, spain]

    @classmethod
    def definitions(cls):
        word_info = []

        # Some words can be both feminine and masculine nouns. In the dictionary, the definition of the word
        # will be divided into several sections based on its part of speech. Therefore, we will use
        # the part of speech as the namespace of the word info.
        namespaces = cls.driver.find_elements(By.CSS_SELECTOR, cls.definition_body_selector)

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

            senses_under_gramGrp = namespace.find_elements(By.CSS_SELECTOR, " .gramGrp > .sense")
            # in this case the .sense lie immediately under '.hom' not under .gramGrp
            definitions = senses_under_gramGrp if senses_under_gramGrp is not None else namespace.find_elements(
                By.CSS_SELECTOR, ".hom > .sense")

            for definition in definitions:
                definition_info = {}
                description = ""
                description_examples = []

                for sense in definition.find_elements(By.XPATH, "./*"):
                    classes = sense.get_attribute("class").split(" ")
                    print(classes)
                    # try to get the word definition (description)
                    if re.search(r'\btype-syn\b', classes) or re.search(r'\bgramGrp\b', classes) or re.search(
                            r'\btype-subj\b', classes) or re.search(
                        r'\btype-translation\b', classes) or re.search(r'\bsense\b', classes) and not re.search(
                        r'\bxr\b', classes):
                        description += sense.text + "\n"

                    # try to get the examples for that definition (description)
                    if "type-example" in sense.get_attribute("class"):
                        quote = sense.find_element(By.CSS_SELECTOR, ".type-example > .quote").text
                        translation = sense.find_element(By.CSS_SELECTOR, ".type-example >.type-translation").text
                        description_examples.append({"quote": quote, "translation": translation})

                    if "type-phr" in sense.get_attribute("class"):
                        quote = sense.find_element(By.CSS_SELECTOR, ".type-phr > .type-phr").text
                        translation = ""
                        try:
                            translation = sense.find_element(By.CSS_SELECTOR, ".type-phr > .type-translation").text
                        except:
                            pass
                        subdefintion = {"quote": quote, "translation": translation, "examples": []}
                        subsexamples = sense.find_elements(By.CSS_SELECTOR, ".type-phr > .type-example")
                        for subexample in subsexamples:
                            subquote = sense.find_element(By.CSS_SELECTOR, ".type-example > .quote").text
                            subtranslation = sense.find_element(By.CSS_SELECTOR,
                                                                ".type-example >.type-translation").text
                            subdefintion["examples"].append({"quote": subquote, "translation": subtranslation})

                        description_examples.append(subdefintion)

                definition_info['description'] = description
                definition_info['examples'] = description_examples
                info_in_namespace['definitions'].append(definition_info)
            # info_in_namespace.append(info_in_namespace)

        # print(info_in_namespace)


if __name__ == '__main__':
    Word.get("final")
    Word.definitions()
