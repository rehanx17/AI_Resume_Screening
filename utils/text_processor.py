import re
import spacy


nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize_text(text):
    doc = nlp(text)

    tokens = []

    for token in doc:
        tokens.append(token.text)

    return tokens


def identify_stopwords(text):
    doc = nlp(text)

    stopwords = []

    for token in doc:
        if token.is_stop:
            stopwords.append(token.text)

    return stopwords

def get_useful_tokens(text):
    doc = nlp(text)

    useful_tokens = []

    for token in doc:
        if not token.is_stop and not token.is_punct:
            useful_tokens.append(token.text)

    return useful_tokens