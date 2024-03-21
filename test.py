import spacy
from spacy.lang.es.examples import sentences

nlp = spacy.load("es_dep_news_trf")
doc = nlp(sentences[0])
print(doc.text)
for token in doc:
    print(token.text, token.pos_, token.dep_)
