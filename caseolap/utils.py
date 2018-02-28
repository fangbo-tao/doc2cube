from pandas import DataFrame as DF
import codecs
from pandas import to_datetime

class Hierarchy:

	def __init__(self):
		self.nid = {}		# node name -> id
		self.ind = {}		# node id -> name
		self.idd = {}		# parent -> [node id]
		self.ipd = {}		# node id -> [parent id]


def load_data(data_file):
	df = DF.from_csv(data_file)
	columns = list(df.columns.values)
	if 'Date' in columns:
		df['Date'] = to_datetime(df['Date'])

	return df

def load_simple_hier(hier_file):
	hier = Hierarchy()
	with open(hier_file) as hf:
		for line in hf:
			arr = line.strip().split("\t")
			hid = int(arr[0])
			phid = int(arr[1])
			att_value = arr[2]

			hier.nid[att_value] = hid
			hier.ind[hid] = att_value
			if phid not in hier.idd:
				hier.idd[phid] = []
				hier.ipd[phid] = []
			if hid not in hier.idd:
				hier.idd[hid] = []
				hier.ipd[hid] = []
			hier.idd[phid].append(hid)
			hier.ipd[hid].append(phid)

	return hier


def load_hier(dim_hier_dict):
	'''
	1. should return a hier relations as a dict
	key must be attributes in data table
	hier['location'] = hier_dict
	2. the values of hier_dict are all the
	descendants of the key, including itself.
	3. hier_dict should contain all the possible
	values of a specific type
	hier_dict[101]=[1,2,3..]
	'''
	hiers = {}
	for dim, file_name in dim_hier_dict.items():
		hier = load_simple_hier(file_name)
		hiers[dim] = hier

	return hiers

def get_all_legal_vals(hier, val):
	'''
	Get all children of current hierarchy node
	'''
	def helper(cur_val):
		if cur_val in all_legal_dict:
			return
		all_legal_dict[cur_val] = 1

		for ch_val in hier.idd[cur_val]:
			helper(ch_val)

	all_legal_dict = {}
	helper(val)

	return all_legal_dict


def get_all_ancestors(hier, val):
	'''
	Get all ancestors of current node
	'''
	all_legal_list = [val]
	while val in hier.ipd and len(hier.ipd[val]) > 0:
		val = hier.ipd[val][0]
		all_legal_list.append(val)

	return all_legal_list

def get_direct_parent(hier, val):
	result = None
	if len(hier.ipd[val]) > 0:
		result = hier.ipd[val][0]
	return result


def get_siblings(hier_dict, val):
	pass	

def load_simple_measure(data_file):
	doc_phrase_measure = {}
	with codecs.open(data_file, "r", encoding="utf-8") as df:
		for line in df:
			arr = line.strip().split(':')
			doc_index = int(arr[0])
			doc_phrase_measure[doc_index] = {}
			for phrase_measure in arr[1].strip().split(','):
				ph_me_arr = phrase_measure.strip().split('|')
				if len(ph_me_arr) < 2:
					continue
				phrase = ph_me_arr[0]
				measure = float(ph_me_arr[1])

				doc_phrase_measure[doc_index][phrase] = measure

	return doc_phrase_measure
