import nltk
nltk.download()
import nltk.data


def splitSentence(paragraph):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(paragraph)
    return sentences

#print("hello world`")
#if __name__ == '__main__':
print(splitSentence("My name is Tom. I am a boy. I like soccer!"))
