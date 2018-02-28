# this class is to try step 2 with simple svm classifier
import numpy as np
# stopwords.words('english'): a list of stopwords
from config import *
from preprocess import *
from sklearn.svm import LinearSVC, SVC
from nltk.classify.scikitlearn import SklearnClassifier
import nltk
import argparse
import string

docs = {} # id:text
classes = set()
golden = {} # id:class
train = {} # id:class

# top features used, -1 means using everything:
feature_cnt = 1000

stopwords = nltk.corpus.stopwords.words('english')

# print nltk.word_tokenize("today, I have a news to tell you that SSF!".translate(None, string.punctuation))

# all_words = nltk.FreqDist(w.lower() for w in movie_reviews.words())
# print movie_reviews.words()
# print all_words


def feature_generation(args):
    print 'start generating features'

    doc_tokens = {}
    doc_features = {}

    # generate vocab
    all_tokens = []
    for did in docs:
        text = docs[did].translate(None, string.punctuation)

        tokens = [w.lower() for w in nltk.word_tokenize(text)]
        # to remove stopwords
        if args.stopwords == 0:
            tokens = [w for w in tokens if w not in stopwords]
        doc_tokens[did] = tokens
        all_tokens.extend(tokens)
    all_tokens = nltk.FreqDist(all_tokens)
    if feature_cnt > 0:
        token_features = list(all_tokens)[:feature_cnt]
    else:
        token_features = list(all_tokens)

    print 'vocab generated: %d' % len(token_features)

    # generate feature map for every document
    for did in docs:
        features = {}
        if args.model == 'nb':
            for token in token_features:
                features[token] = False
            for token in doc_tokens[did]:
                if token in features:
                    features[token] = True
        elif args.model == 'svm':
            # TODO: add svm model here
            for token in token_features:
                features[token] = False
            for token in doc_tokens[did]:
                if token in features:
                    features[token] += 1
        else:
            print 'Model ' + args.model + ' is not supported.'
            exit(1)
        doc_features[did] = features

    print 'featureset generated'

    train_set = []
    test_set = []
    doc_ids_in_test = []
    for did in docs:
        if did in train:
            train_set.append((doc_features[did], train[did]))
        else:
            test_set.append((doc_features[did], golden[did]))
            doc_ids_in_test.append(did)

    print 'classifier starts training'

    if args.model == 'nb':
        classifier = nltk.NaiveBayesClassifier.train(train_set)
    elif args.model == 'svm':
        classifier = SklearnClassifier(LinearSVC(), sparse=False).train(train_set)

    print 'classifier trained'

    # print(nltk.classify(classifier, test_set))
    with open(step2_error_file, 'w+') as g:
        for index, did in enumerate(doc_ids_in_test):
            features = test_set[index][0]
            predicted = classifier.classify(features)
            gold = test_set[index][1]
            g.write(did + '\t' + predicted + '\t' + gold + '\t' + str(predicted==gold) + '\n')

    print(nltk.classify.accuracy(classifier, test_set))

def preprocessing():
    
    read_docs(docs_file, docs)
    read_cell_file(cell_file, classes, golden, docs)
    read_step1_classified_docs(step1_file, train, docs)


def main(args):

    # read data
    preprocessing()

    # using nltk to generate features
    feature_generation(args)



parser = argparse.ArgumentParser(description='.')
parser.add_argument('-type', dest='type', type=int,
                    default=1, help='type 1: words, type 2: phrases')
parser.add_argument('-stopwords', dest='stopwords', type=int,
                    default=0, help='1 means keep stopwords')
parser.add_argument('-model', dest='model', type=str,
                    default='svm', help='svm or nb')


args = parser.parse_args()

# sample command: python svm.py -model svm
main(args)