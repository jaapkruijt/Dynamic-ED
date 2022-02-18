from stanza.server import CoreNLPClient

if __name__ == "__main__":
    text = "Jaap is testing out some stuff. He is not sure it will work"
    with CoreNLPClient(
            annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref'],
            file='friends_s01e01sc1.conll',
            timeout=30000,
            memory='6G',
            properties={"parse-model":'neural-english-conll.properties'}) as client:
        ann = client.annotate(text)
    print(ann.corefChain)
