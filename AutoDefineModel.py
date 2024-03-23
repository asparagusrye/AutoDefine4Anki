from typing import List
from Dictionary.ESPCollins import Word
import csv


class AutoDefineModel:
    def __init__(self):
        self.list_of_words = []

    def add_word(self, name, definitions, audio):
        self.list_of_words.append([name, definitions, audio])

    def add_words(self, keywords: List[str]):
        for keyword in keywords:
            Word.get(keyword)
            word_info = Word.info()
            # TODO: Fix sometimes the word has only one pronunciation audio e.g. chava or doesn't have at all
            pronunciation_url = ""
            try:
                pronunciation_url = word_info["pronunciations"]["Spain"]
            except:
                pass
            self.add_word(word_info["name"], word_info["definitions_in_html"], pronunciation_url)

    def export_to_csv(self):
        with open('D:/export.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerows(self.list_of_words)
