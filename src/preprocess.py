import re
import nltk
import string

doc_splitter = ' TTTAATTT '

def parse_one_doc(text):
    # read article text and return tokenized result
    stopwords = nltk.corpus.stopwords.words('english')
    text = text.replace('.', '. ')
    text = text.replace('###', 'jzaq')
    text = text.replace('-', 'wias')
    text = text.translate(None, string.punctuation)
    tokens = [w.lower() for w in nltk.word_tokenize(text)]
    tokens = [w.replace('jzaq', '###').replace('wias', '-') for w in tokens if w not in stopwords]
    # text = re.sub(r'"|:', r' ', text)
    # text = re.sub(r' +', r' ', text)
    # text = re.sub(r'([0-9a-zA-Z]) \.', r'\1.', text)
    # tokens = text.split(' ')
    return tokens

def parse_all_docs(texts):

    text = doc_splitter.join(texts)

    stopwords = nltk.corpus.stopwords.words('english')
    text = text.replace('.', '. ')
    text = text.replace('###', 'jzaq')
    text = text.replace('-', 'wias')
    text = text.translate(None, string.punctuation)
    tokens = [w.lower() for w in nltk.word_tokenize(text)]
    tokens = [w.replace('jzaq', '###').replace('wias', '-') for w in tokens if w not in stopwords]

    token_lists = []
    t_list = []
    for token in tokens:
        if token != doc_splitter:
            t_list.append(token)
        else:
            token_lists.append(t_list)
            t_list = []

    return token_lists



def read_docs(filename, docs, simp_phrase=True, tokenize=False):
    # read all docs text into a map for .data file
    with open(filename, 'r+') as f:
        index = 1
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            text = segments[2].replace('.', '. ')

            if tokenize:
                stopwords = nltk.corpus.stopwords.words('english')
                # if the output is tokenzized
                text = text.replace('###', 'jzaq')
                text = text.replace('-', 'wias')
                text = text.translate(None, string.punctuation)
                tokens = [w.lower() for w in nltk.word_tokenize(text)]
                tokens = [w.replace('jzaq', '###').replace('wias', '-') for w in tokens if w not in stopwords]
                # text = re.sub(r'"|:', r' ', text)
                # text = re.sub(r' +', r' ', text)
                # text = re.sub(r'([0-9a-zA-Z]) \.', r'\1.', text)
                # tokens = text.split(' ')
                docs[str(index)] = tokens
                # return

            else: 
                if simp_phrase:
                    text = text.replace('###', ' ')
                else:
                    text = text.replace('###', '_')
                text = re.sub(r'"|:', r' ', text)
                text = re.sub(r' +', r' ', text)
                text = re.sub(r'([0-9a-zA-Z]) \.', r'\1.', text)
                docs[str(index)] = text
            index += 1

def read_emb_file(filename, embedding_map, have_meta=True):
    # read embedding file
    first_line = True if have_meta else False
    vocab = dim = 0
    with open(filename, 'r+') as f:
        for line in f:
            if first_line:
                first_line = False
                elems = line.strip('\r\n ').split(' ')
                vocab = int(elems[0])
                dim = int(elems[1])
                continue
            elems = line.strip('\r\n ').split(' ')
            token = elems[0]
            emb = [float(v) for v in elems[1:]]
            embedding_map[token] = emb


def read_seed_file(filename):
    seeds_map = {}
    with open(filename, 'r+') as f:
        for line in f:
            elems = line.strip('\r\n ').split('\t')
            label = elems[0]
            seeds = elems[1].split(' ')
            seeds = [w.replace('_', '###') for w in seeds]
            seeds_map[label] = seeds

    return seeds_map



def read_cell_file(filename, classes, golden, all_docs):
    # read all docs with label 
    with open(filename, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            did, c_label = segments[0], segments[1]
            classes.add(c_label)
            if did not in all_docs:
                print 'Error: document does not exist!!'
                exit(1)
            golden[did] = c_label


def read_step1_classified_docs(filename, target_map, all_docs):
    # read the step 1 classified docs
    with open(filename, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            did, c_label = segments[0], segments[1]
            if did not in all_docs:
                print 'Error: document does not exist!!'
                exit(1)
            target_map[did] = c_label


def read_step1_phrases(filename, target_map):
    # read the step 1 phrases, target_map: {cell: set of phrases}
    with open(filename, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            cell, phrases = segments[0], segments[1]
            phrases = set(phrases.split(' '))
            target_map[cell] = phrases


def get_13000_docs():

    folder = 'data_news/'
    map_f = folder + 'd40000to10000_mapping.txt'
    text_f = folder + 'used/docs_parsed.txt'
    o_f = folder + 'docs13000seg.txt'

    with open(o_f, 'w+') as g:
        ori_docs = []
        doc_map = {} # new_id : old_id

        with open(text_f) as f:
            ori_docs = [l for l in f]


        with open(map_f) as f:
            for line in f:
                o_id, n_id = [int(x) for x in line.strip('\r\n').split('\t')]
                doc_map[n_id] = o_id

        for i in range(13081):
            text = ori_docs[doc_map[i]]
            g.write(text)



