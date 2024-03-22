import spacy
nlp = spacy.load("es_dep_news_trf")
doc = nlp("Esto es una frase.")
print([(w.text, w.pos_) for w in doc])
