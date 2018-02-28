from caseslim import CaseSlim
from cell import Cell, Document
import operator
from config import *
import ipdb
import argparse


folder = '../data/caseolap/'




# seeds
# all the cells
cells = {}
docs = {}
# Document ids
handled_docs = set()
# doc-phrases...


# Expand document related params
smooth_fac = 0.01
# doc_minimum = 5
# doc_maximum = 5
doc_added = 5
doc_thres = 0.95



def caseOLAP():

    phrase_added = 5
    phrase_thres = 1.0

    freq_data = {}
    for did in handled_docs:
        freq_data[did] = docs[did].phrases

    print str(len(handled_docs))

    cid_dids = {}
    for c_label in cells:
        c = cells[c_label]
        # 
        cid_dids[c_label] = [doc.id for doc in c.docs]


    # generate representative phrases in each enriched cell
    for cell in cid_dids:
        print 'Cell: %s, doc size: %d' % (cell, len(cid_dids[cell]))
        selected_docs = cid_dids[cell]
        context_doc_groups = {}
        for cell_2 in cid_dids:
            if cell_2 != cell:
                context_doc_groups[cell_2] = cid_dids[cell_2]
        caseslim = CaseSlim(freq_data, selected_docs, context_doc_groups)
        # caseslim = CaseSlim(freq_data, selected_docs, all_context_group)
        top_phrases = caseslim.compute()
        phr_str = ' '.join([ph[0] + '|' + str(ph[1]) for ph in top_phrases])

        # print cells[cell].seeds
        # print '\n'
        # add phrases into the seeds
        added = 0
        for phr in top_phrases:
            score = phr[1]
            text = phr[0]
            if score < phrase_thres:
                break
            if added < phrase_added and text not in cells[cell].seeds:
                cells[cell].seeds.add(text)
                added += 1
                print 'added ' + text + '(' + str(score) + ')' + ' for ' + cell

            # print 'added ' + text + ' for cell ' + cell

    print '\n\n'



def expand_docs_v2(classify_all=False):
    """
    Version_2 for expanding documents:
    score(d,c) = smooth_fac + #(d, c_seeds)
    score(d,c) = score(d,c) / \sigma_{score(d,c)}
    """

    all_seeds = set()
    # structure: cell label => map of doc and score.
    doc_cell_score = {}
    for c_label in cells:
        c = cells[c_label]
        all_seeds = all_seeds | c.seeds
        doc_cell_score[c_label] = {}

    
    for did in docs:
        if did in handled_docs:
            continue
        doc = docs[did]
        for c_label in cells:
            c = cells[c_label]
            positive_phrases = c.seeds
            score = smooth_fac
            for phr in doc.phrases:
                if phr in positive_phrases:
                    score += doc.phrases[phr]
            doc_cell_score[c_label][did] = score

    for did in docs:
        if did in handled_docs:
            continue
        doc = docs[did]
        total = 0
        for c_label in cells:
            total += doc_cell_score[c_label][did]

        for c_label in cells:
            doc_cell_score[c_label][did] = float(
                doc_cell_score[c_label][did]) / total

    if classify_all:
        no_signal = 0
        correct = 0
        incorrect = 1
        test_docs = {}
        for did in docs:
            if did in handled_docs:
                continue
            doc = docs[did]

            map_by_cell = {}
            for c_label in cells:
                map_by_cell[c_label] = doc_cell_score[c_label][did]

            sorted_by_cell = sorted(map_by_cell.items(), 
                                key=operator.itemgetter(1), reverse=True)

            if sorted_by_cell[0][1] == sorted_by_cell[1][1] and sorted_by_cell[0][1] == 0.125:
                test_docs[doc] = 'None'
                no_signal += 1
            elif doc.fact_cell.label == sorted_by_cell[0][0]:
                test_docs[doc] = sorted_by_cell[0][0]
                correct += 1
            else:
                test_docs[doc] = sorted_by_cell[0][0]
                incorrect += 1


        print 'no signal: ' + str(no_signal)
        print 'correct: ' + str(correct)
        print 'incorrect: ' + str(incorrect)
        print 'precision: ' + str(float(correct)/(correct + incorrect + no_signal))

        with open(step1_direct_class_file, 'w+') as g:
            for doc in test_docs:
                g.write(str(doc.id) + '\t' + test_docs[doc] + '\t' + doc.fact_cell.label + '\t'
                    + str(test_docs[doc] == doc.fact_cell.label) + '\n')

        return

    # rank the scores of docs in each cell
    for c_label in cells:
        c = cells[c_label]

        doc_scores = doc_cell_score[c_label]
        sorted_docs = sorted(doc_scores.items(),
                             key=operator.itemgetter(1), reverse=True)

        added_cnt = 0
        least_score = 1

        # for doc_pair in sorted_docs[:doc_maximum]:
        #     did = doc_pair[0]
        #     score = doc_pair[1]
        #     to_add = False
        #     if added_cnt < doc_minimum:
        #         to_add = True
        #     elif score >= doc_thres:
        #         to_add = True
        #     if to_add:
        #         doc = docs[did]
        #         doc.exp_cell = c
        #         c.docs.add(doc)
        #         handled_docs.add(doc.id)
        #         added_cnt += 1
        #         least_score = score
        
        for doc_pair in sorted_docs[:doc_added]:
            did = doc_pair[0]
            score = doc_pair[1]
            if score >= doc_thres:
                doc = docs[did]
                doc.exp_cell = c
                c.docs.add(doc)
                handled_docs.add(doc.id)
                added_cnt += 1
                least_score = score

        print "added " + str(added_cnt) + ' with least score ' + str(least_score) + " for " + c_label + '(' + str(len(c.seeds)) + ')'

        #(sorted_docs[:doc_added])

    evaluate_precision()
    print '\n'

def expand_docs():
    # input: current assigned docs of each cell
    # output: rank list of docs in each cell

    # compute the score of each cell
    all_seeds = set()
    # structure: cell label => map of doc and score.
    doc_cell_score = {}
    for c_label in cells:
        c = cells[c_label]
        all_seeds = all_seeds | c.seeds
        doc_cell_score[c_label] = {}

    for did in docs:
        if did in handled_docs:
            continue

        doc = docs[did]
        for c_label in cells:
            c = cells[c_label]
            positive_phrases = c.seeds
            score = 0
            for phr in doc.phrases:
                if phr in positive_phrases:
                    score += doc.phrases[phr]
                elif phr in all_seeds:
                    score -= doc.phrases[phr]
            doc_cell_score[c_label][did] = score

    # rank the scores of docs in each cell
    for c_label in cells:
        c = cells[c_label]

        doc_scores = doc_cell_score[c_label]
        sorted_docs = sorted(doc_scores.items(),
                             key=operator.itemgetter(1), reverse=True)

        added_cnt = 0
        for doc_pair in sorted_docs[:doc_added]:
            did = doc_pair[0]
            score = doc_pair[1]
            if score >= doc_thres:
                doc = docs[did]
                doc.exp_cell = c
                c.docs.add(doc)
                handled_docs.add(doc.id)
                added_cnt += 1

    evaluate_precision()


def preprocessing(seed):
    # Step 1: read seeds and entire phrase list into memory
    with open(phrase_file, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            c_label = segments[0]
            c_top_phrases = segments[1].split(' ')
            if c_label in cells:
                print 'Error: cell duplicated!!'
                exit(1)

            cells[c_label] = Cell(c_label)
            c = cells[c_label]
            for t_phrase in c_top_phrases:
                elems = t_phrase.split('|')
                phr = elems[0]
                score = float(elems[1])
                c.fact_phrases[phr] = score

    with open(seed_file, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            c_label = segments[0]
            c_seed_phrases = segments[1].split(' ')

            if c_label not in cells:
                print 'Error: cell does not exist!!'
                exit(1)

            c = cells[c_label]
            if seed != -1:
                c_seed_phrases = c_seed_phrases[:seed]

            for phrase in c_seed_phrases:
                c.seeds.add(phrase)

    # Step 2: read doc-phrase map into memory
    with open(doc_phrase_file, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split(' ')
            did = int(segments[0])
            if did in docs:
                print 'Error: document duplicated!!'
                exit(1)
            doc = Document(did)
            docs[did] = doc
            for i in range(1, len(segments)):
                elems = segments[i].split('|')
                phr, count = elems[0], int(elems[1])
                doc.phrases[phr] = count

    # Step 3: read doc-cell facts into memory
    with open(cell_file, 'r+') as f:
        for line in f:
            segments = line.strip('\r\n ').split('\t')
            did, c_label = int(segments[0]), segments[1]
            if did not in docs:
                print 'Error: document does not exist!!'
                exit(1)
            if c_label not in cells:
                print 'Error: cell does not exist!!'
                exit(1)
            doc = docs[did]
            c = cells[c_label]
            doc.fact_cell = c
            c.fact_docs.add(c)

    # output some stuff
    print 'Imported ' + str(len(cells)) + ' cells'
    print 'Imported ' + str(len(docs)) + ' documents'


def evaluate_precision():
    # evaluate the expansion performance
    total = 0
    correct_cnt = 0

    for c_label in cells:
        c = cells[c_label]
        for doc in c.docs:
            total += 1
            if doc.fact_cell == doc.exp_cell:
                correct_cnt += 1

    print 'total count: ' + str(total)
    print 'precision: ' + str(float(correct_cnt) / total)


def empty_cell_docs():
        # to reset cell docs if the new phrases are added
    for did in handled_docs:
        doc = docs[did]
        doc.exp_cell = None

    for c_label in cells:
        c = cells[c_label]
        c.docs = set()


def output_result():
    with open(step1_file, 'w+') as g:
        for c_label in cells:
            c = cells[c_label]
            for doc in c.docs:
                g.write(str(doc.id) + '\t' + c.label + '\t' + doc.fact_cell.label + '\t'
                    + str(c == doc.fact_cell) + '\n')

    with open(step1_phrases_file, 'w+') as g:
        for c_label in cells:
            c = cells[c_label]
            g.write(c_label + '\t' + ' '.join(c.seeds) + '\n')

    evaluate_precision()




def main(args):

    # main logic..
    preprocessing(args.seed)

    # start iterating the process
    for i in range(args.iter):
        print '============ Interation: ' + str(i)
        if args.doc_expm == 2:
            expand_docs_v2()
        elif args.doc_expm == 1:
            expand_docs()
        else:
            print 'document expansion param wrong.'
            exit(1)
        
        caseOLAP()

    if args.classify:
        expand_docs_v2(classify_all=True)

    output_result()



parser = argparse.ArgumentParser(description='.')
parser.add_argument('-iter', dest='iter', type=int,
                    default=max_iter)
parser.add_argument('-doc', dest='doc_expm', type=int,
                    default=default_doc_expm)
parser.add_argument('-seed', dest='seed', type=int,
                    default=init_seed_cnt)
parser.add_argument('-classify', dest='classify', type=bool,
                    default=False)

args = parser.parse_args()

# sample command: 
# python expander.py -iter 6
main(args)
