

# the class to store the current constructed cells
class Cell:

    def __init__(self, label):
        self.label = label
        self.seeds = set()
        # the caseolap result from real cell, key: phrase, value: caseolap
        # score
        self.fact_phrases = {}
        # the constructed documents, Document instances
        self.docs = set()
        # the ground truth documents, Document instances
        self.fact_docs = set()


class Document:

    def __init__(self, did):
        self.id = did
        # phrases in docs, key: phrase. value: count
        self.fact_cell = None
        self.exp_cell = None
        self.phrases = {}


class Token:

    def __init__(self, text):
        self.text = text



