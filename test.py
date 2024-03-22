import stanza

nlp = stanza.Pipeline(lang="es", processors='tokenize,mwt,pos,lemma',
                      download_method=stanza.DownloadMethod.REUSE_RESOURCES)
doc = nlp('Este es un gato.')
print(*[f'word: {word.text + " "}\tlemma: {word.lemma}' for sent in doc.sentences for word in sent.words], sep='\n')
