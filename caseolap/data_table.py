from utils import load_data, load_hier, get_all_legal_vals

class DataTable:
	
	def __init__(self, data_file, hier_meta_dict):
		self.records = load_data(data_file)
		self.hiers = load_hier(hier_meta_dict)


	def doc_count(self, args):
		sliced = self.slice(args)
		return len(sliced['DocID'])
		# return sliced['DocID']


	def slice(self, args):
		sliced = self.records
		
		for attr, val in args.items():
			if attr == "Date":
				print "do not support date for now"
			else:
				val_id = self.hiers[attr].nid[val]
				legal_vals = get_all_legal_vals(self.hiers[attr], val_id)
				sliced = sliced.loc[sliced[attr].isin(legal_vals)]

		return sliced.copy()

	def slice_and_return_doc_id(self, args):
		sliced = self.slice(args)
		return sliced['DocID']

	def slice_and_return_parents(self, query):
		sliced = self.records
		result_contexts = {}
		if len(query.items()) == 1:
			return {'all':[-1]}
			#return [[-1]]	
		for attr_2, val_2 in query.items():
			sliced = self.records
			query_copy = query.copy()
			cell_name = ''
			for attr, val in query_copy.items():
				if attr_2 != attr:
					cell_name += attr + "_" + str(val) + "_"
					val_id = self.hiers[attr].nid[val]
					legal_vals = get_all_legal_vals(self.hiers[attr], val_id)
					sliced = sliced.loc[sliced[attr].isin(legal_vals)]
			result_contexts[cell_name] = sliced['DocID']

		return result_contexts#[x['DocID'] for x in result_contexts]			


	def slice_and_return_siblings(self, query):
		sliced = self.records
		result_contexts = {}
			
		for attr, val in query.items():
			hier = self.hiers[attr]
			val_ori_id = hier.nid[val]
			sibling_ids = hier.idd[hier.ipd[val_ori_id][0]]
			# print attr
			# sib_names = [hier.ind[x] for x in sibling_ids]
			# print sib_names
			query_copy = query.copy()
			print val_ori_id
			for sid in sibling_ids:
				s_name = hier.ind[sid]
				sliced = self.records
				if sid == val_ori_id:
					continue
				cell_name = ''
				for attr2, val2 in query_copy.items():
					if attr2 == attr:
						val_id = sid
						value = s_name
					else:
						val_id = self.hiers[attr2].nid[val2]
						value = val2
					cell_name += attr2 + "|" + value + ";"
					legal_vals = get_all_legal_vals(self.hiers[attr2], val_id)
					sliced = sliced.loc[sliced[attr2].isin(legal_vals)]
				
				if len(sliced['DocID']) > 0:
					result_contexts[cell_name] = sliced['DocID']

		return result_contexts#[x['DocID'] for x in result_contexts]

