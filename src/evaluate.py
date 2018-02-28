import sys
import math
import copy
import operator
import numpy as np
sys.path.append('../../')
import preprocess
import utils
from label_hierarchy import Hierarchy
from read_files import *
import argparse

ntypes = ['d', 'l', 'p']
hier = None
pmode = None
emode = None
target_dim = 0
true_file = None


def load_dp(dp_file, reverse=True):

	result_map = {}
	with open(dp_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			if reverse:
				if segs[1] not in result_map:
					result_map[segs[1]] = set()
				result_map[segs[1]].add(segs[0])

	return result_map

def load_edge_map(edge_file):
	
	result_map = {}
	with open(edge_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			if segs[0] not in result_map:
				result_map[segs[0]] = {}
			result_map[segs[0]][segs[1]] = float(segs[2])

	return result_map

def distance_q(source_type, target_type, embs, e_size):
	# if pmode=COS, then using cossim to evaluate the distance
	# if pmode=DOT, then using dot product to evaluate the distance


	target_pool = copy.copy(embs[target_type])
	# if mode == 'Het':
	# 	target_pool = {}
	# 	for n_type in ntypes:
	# 		target_pool.update(embs[n_type])

	while 1:
		n_name = raw_input("Enter your node: ")
		if n_name in embs[source_type]:
			print 'looking for ' + n_name + '...'
			t_emb = embs[source_type][n_name]
			sim_map = {}
			for key in target_pool:
				if pmode == 'COS':
					sim_map[key] = utils.cossim(t_emb, target_pool[key])
				if pmode == 'DOT':
					sim_map[key] = utils.dot_product(t_emb, target_pool[key])
			sim_map = sorted(sim_map.items(), key=operator.itemgetter(1), reverse=True)
			print sim_map[:10]

		else:
			print 'name ' + n_name + ' is not fould in ' + source_type


def expan(embs, l_prel_file, dp_file, lp_file, mode='EMB'):
	# the part to verify iterative expansion
	# Mode = EMB: meaning that the similarity is learned from embedding
	# Mode = DIS: meaning that the similarity is from L-P assignment

	target_type = 'p'
	source_type = 'l'
	multiplier = 5
	thre_softmax = 0.5

	ori_embs = embs
	agg_embs = copy.copy(embs)
	pd_map = load_dp(dp_file, reverse=True)
	dp_map = load_edge_map(dp_file)
	lp_map = load_edge_map(lp_file)
	dist_map = {x:1 for x in embs[target_type]}
	vec_size = 0
	for d in ori_embs[target_type]:
		vec_size = len(ori_embs[target_type][d])
		break

	seeds_map = {}	# label : seed set
	all_seeds = set()
	with open(l_prel_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			if segs[1] == '*':
				continue
			seeds_map[segs[1]] = set()
			seeds_map[segs[1]].add(segs[2].lower())
			all_seeds.add(segs[2].lower())	

	print '*********** Direct Embedding'
	evaluate(ori_embs, true_file, target_dim)

	agg_embs[source_type] = weighted_avg_embedding(lp_map, agg_embs[target_type], dist_map, vec_size)
	agg_embs['d'] = weighted_avg_embedding(dp_map, agg_embs[target_type], dist_map, vec_size)

	print '*********** Aggregate without expansion'
	evaluate(agg_embs, true_file, target_dim)

	for i in range(2):
		print '======== iter ' + str(i) + ' of expansion.'
		extended_seeds = expan_round(agg_embs, seeds_map, all_seeds, 3, 1, mode=mode, pd_map=pd_map)
		print '============= seeds expanded'

		for seed in extended_seeds:
			label, phrase = seed.split('@')
			if label not in lp_map or phrase in lp_map[label]:
				print 'ERRRROR!!! ' + seed
			all_seeds.add(phrase.lower())
			seeds_map[label].add(phrase.lower())
			lp_map[label][phrase] = 1

		agg_embs[source_type] = weighted_avg_embedding(lp_map, agg_embs[target_type], dist_map, vec_size)

		print '*********** Aggregate with expansion at iter ' + str(i)
		evaluate(agg_embs, true_file, target_dim)

	normal = False
	source_type = 'd'
	target_type = 'l'
	mid_type = 'p'

	for i in range(2):

		if i > 0:
			normal = True

		print '============= iter ' + str(i) + ' of dist started.'

		pred_label, doc_score = doc_assignment(agg_embs, 'd', 'l')
		top_labels = [w.path for w in hier.get_nodes_at_level(1)]

		print '============= docs assigned to labels'

		# # print meta stats
		# top_label_cnts = {}
		# for label in top_labels:
		# 	top_label_cnts[label] = 0
		# for doc_pair in filtered_docs:
		# 	l = pred_label[doc_pair[0]]
		# 	top_label_cnts[l] += 1
		# print top_label_cnts
		# print 'top level labels: ' + str(top_labels)

		label_to_idx = {}
		for idx, label in enumerate(top_labels):
			label_to_idx[label] = idx
		uniform_vec = [1.0/len(top_labels)] * len(top_labels)
		# print uniform_vec
		label_to_doc = {}
		
		for label in top_labels:
			label_to_doc[label] = set()


		docs_used = {}

		if normal:
			print 'used docs in reweighting: ' + str(len(pred_label))
			for doc, score in doc_score.iteritems():
				label_to_doc[pred_label[doc]].add(doc)
		else:
			for label in top_labels:
				p = label.lower()
				# idx = label_to_idx[label]
				for doc in pd_map[p]:
					label_to_doc[label].add(doc)
					if doc not in docs_used:
						docs_used[doc] = set()
					docs_used[doc].add(label)
			print 'docs used: %d' % len(docs_used)


		cnt_vec = [0.0] * len(top_labels)
		for label in label_to_doc:
			cnt_vec[label_to_idx[label]] = len(label_to_doc[label])
		comp_vec = utils.l1_normalize(cnt_vec)

		print cnt_vec

		# print comp_vec

		distinct_map = {}
		
		if normal:
			for phrase in embs[mid_type]:
				p_vec = [0.0] * len(top_labels)

				# if len(pd_map[phrase]) < 100:
				# 	continue

				for doc in pd_map[phrase]:
					idx = label_to_idx[pred_label[doc]]
					p_vec[idx] += 1.0
				
				if sum(p_vec) == 0:
					print 'ERROR!!!!!!!!!!'
					continue

				p_vec = utils.l1_normalize(p_vec)

				# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
				kl = utils.kl_divergence(p_vec, uniform_vec)
				# kl = utils.kl_divergence(p_vec, comp_vec)
				distinct_map[phrase] = kl
		else:
			for phrase in embs[mid_type]:
				p_vec = [0.0] * len(top_labels)

				# if len(pd_map[phrase]) < 100:
				# 	continue

				for doc in pd_map[phrase]:
					if doc in docs_used:
						for label in docs_used[doc]:
							idx = label_to_idx[label]
							p_vec[idx] += 1.0

				# print p_vec
				
				if sum(p_vec) == 0:
					distinct_map[phrase] = 0
					# print 'ERROR!!!!!!!!!!'
					continue
				
				# p_vec = [x / cnt_vec[i] for i, x in enumerate(p_vec)]


				p_vec = utils.l1_normalize(p_vec)

				# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
				# kl = utils.kl_divergence(p_vec, uniform_vec)
				kl = utils.kl_divergence(p_vec, comp_vec)
				distinct_map[phrase] = kl

		dist_map = distinct_map
		with open('focal_comp.txt', 'w+') as g:
			for (ph, score) in sorted(dist_map.items(), key=operator.itemgetter(1), reverse=True):
				g.write('%s,%f\t' % (ph, score))

		print '============= phrase distinctness computed.'

		agg_embs[source_type] = weighted_avg_embedding(dp_map, agg_embs[mid_type], dist_map, vec_size)
		print '============= doc embedding aggregated.'

		print '*********** Aggregate with distinct at iter ' + str(i)
		evaluate(agg_embs, true_file, target_dim)


	return


def expan_round(embs, seeds_map, all_seeds, limit, cate_lim, mode='EMB', pd_map=None):

	target_type = 'p'

	multiplier = 5
	thre_softmax = 0.5

	extended_seeds = set()
	candidates = {}

	if mode == 'EMB':
		for phrase in embs[target_type]:
			if phrase in all_seeds:
				continue
			t_emb = embs[target_type][phrase]
			rel_values = {}
			# flat comparison
			for label in seeds_map:
				max_sim = 0
				for seed in seeds_map[label]:
					sim = multiplier * utils.cossim(t_emb, embs[target_type][seed])
					if sim > max_sim:
						max_sim = sim
				rel_values[label] = max_sim

			utils.softmax_for_map(rel_values)
			best_label = sorted(rel_values.items(), key=operator.itemgetter(1), reverse=True)[0][0]
			candidates[best_label + '@' + phrase] = rel_values[best_label]
	
	elif mode == 'DIS':
		pred_label, doc_score = doc_assignment(embs, 'd', 'l', mode='FLAT')
		top_labels = [w.path for w in hier.get_all_nodes()]
		print 'Doc Assignment done...'

		label_to_idx = {}
		for idx, label in enumerate(top_labels):
			label_to_idx[label] = idx
		# print uniform_vec
		label_to_doc = {}
		
		for label in top_labels:
			label_to_doc[label] = set()
		for doc, score in doc_score.iteritems():
			label_to_doc[pred_label[doc]].add(doc)
		cnt_vec = [0.0] * len(top_labels)
		for label in label_to_doc:
			cnt_vec[label_to_idx[label]] = len(label_to_doc[label])
		comp_vec = utils.l1_normalize(cnt_vec)

		uniform_vec = [1.0/len(top_labels)] * len(top_labels)
		# print cnt_vec
		# print comp_vec

		for phrase in embs['p']:
			if phrase in all_seeds:
				continue

			p_vec = [0.0] * len(top_labels)

			for doc in pd_map[phrase]:
				idx = label_to_idx[pred_label[doc]]
				p_vec[idx] += 1.0

			max_label_value = 0
			best_label = ''
			best_cnt = 0
			for label in top_labels:
				idx = label_to_idx[label]
				if p_vec[idx] > 0:
					norm_value = p_vec[idx] / cnt_vec[idx]
					if norm_value > max_label_value:
						max_label_value = norm_value
						best_label = label
						best_cnt = p_vec[idx]

			if sum(p_vec) == 0:
				print 'ERROR!!!!!!!!!!'
				continue
			p_vec = utils.l1_normalize(p_vec)
			# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
			# kl = utils.kl_divergence(p_vec, comp_vec)
			kl = utils.kl_divergence(p_vec, uniform_vec)

			# best_label = sorted(rel_values.items(), key=operator.itemgetter(1), reverse=True)[0][0]
			pop = max_label_value
			# * (1 + math.log(1 + max_label_value))
			candidates[best_label + '@' + phrase] = kl * max_label_value

	candidates = sorted(candidates.items(), key=operator.itemgetter(1), reverse=True)

	# cands_by_label = {}
	# for cand in candidates:
	# 	label, phrase = cand.split('@')
	# 	if label not in cands_by_label:
	# 		cands_by_label[label] = {}
	# 	cands_by_label[label][phrase] = candidates[cand]

	# for label in cands_by_label:
	# 	print '\n' + label
	# 	cand_cate = cands_by_label[label]
	# 	best_exps = sorted(cand_cate.items(), key=operator.itemgetter(1), reverse=True)[:10]
	# # best_exps = sorted(candidates.items(), key=operator.itemgetter(1), reverse=True)[:30]
	# 	print best_exps

	# exit(1)

	added = 0
	added_cates = {}
	for (cand, score) in candidates:
		label, phrase = cand.split('@')
		if label not in added_cates:
			added_cates[label] = 0
		if added_cates[label] >= cate_lim:
			continue
		if len(seeds_map[label]) >= 3:
			continue
		extended_seeds.add(cand)
		added_cates[label] += 1
		added += 1
		if added > limit:
			break

	print 'extended: ' + str(extended_seeds)
	return extended_seeds
	


def doc_assignment(embs, source_type, target_type, mode='TOP', hierr=None):
	# mode = TOP, only assign docs to top label
	# mode = FLAT, assign docs to fine-grained level

	target_embs = embs[target_type]
	pred_label = {}
	doc_score = {}
	ratio = 1

	for doc in embs[source_type]:
		doc_emb = embs[source_type][doc]
		sim_map = classify_doc(doc_emb, target_embs)
		if mode == 'TOP':
			pred_label[doc] = hier.get_node(sim_map[0][0]).get_ascendant(1).path
		elif mode == 'FLAT':
			pred_label[doc] = hier.get_node(sim_map[0][0]).path
		doc_score[doc] = sim_map[0][1]

	return pred_label, doc_score	

def weighted_avg_embedding_1(bi_map, embs_from, dist_map, vec_size):
	result_emb = {}
	for d in bi_map:
		ele_map = bi_map[d]
		new_emb = utils.avg_emb_with_distinct(ele_map, embs_from, dist_map, vec_size)
		result_emb[d] = new_emb

	return result_emb


def weighted_avg_embedding(bi_map, embs_from, dist_map, vec_size):
	result_emb = {}
	embs_from_np = {}
	for key in embs_from:
		embs_from_np[key] = np.array(embs_from[key])

	for d in bi_map:
		ele_map = bi_map[d]
		new_emb = utils.avg_emb_with_distinct_1(ele_map, embs_from_np, dist_map, vec_size)
		result_emb[d] = new_emb.tolist()

	return result_emb


def reweight(embs, dp_file, lp_file):
	source_type = 'd'
	target_type = 'l'
	mid_type = 'p'

	ori_embs = embs
	agg_embs = copy.copy(embs)

	# Step 0: check original embedding's performance
	print '*********** Direct Embedding'
	evaluate(ori_embs, true_file, target_dim)

	pd_map = load_dp(dp_file, reverse=True)
	dp_map = load_edge_map(dp_file)
	lp_map = load_edge_map(lp_file)
	dist_map = {x:1 for x in embs[mid_type]}
	vec_size = 0
	for d in ori_embs[mid_type]:
		vec_size = len(ori_embs[mid_type][d])
		break

	# print '============= dp, pd maps loaded'


	# Step 1: check with D weighted avg, what's the performance
	agg_embs[source_type] = weighted_avg_embedding(dp_map, agg_embs[mid_type], dist_map, vec_size)

	# optional L - embedding also aggregated from P
	normal = False

	if not normal:
		agg_embs[target_type] = weighted_avg_embedding(lp_map, agg_embs[mid_type], dist_map, vec_size)


	# print '============= doc embedding aggregated.'

	print '*********** Aggregate iter 0'
	evaluate(agg_embs, true_file, target_dim)

	

	for i in range(2):

		if i > 0:
			normal = True

		print '============= iter ' + str(i+1) + ' of dist started.'

		pred_label, doc_score = doc_assignment(agg_embs, source_type, target_type)
		top_labels = [w.path for w in hier.get_nodes_at_level(1)]

		# print '============= docs assigned to labels'

		# # print meta stats
		# top_label_cnts = {}
		# for label in top_labels:
		# 	top_label_cnts[label] = 0
		# for doc_pair in filtered_docs:
		# 	l = pred_label[doc_pair[0]]
		# 	top_label_cnts[l] += 1
		# print top_label_cnts
		# print 'top level labels: ' + str(top_labels)

		label_to_idx = {}
		for idx, label in enumerate(top_labels):
			label_to_idx[label] = idx
		uniform_vec = [1.0/len(top_labels)] * len(top_labels)
		# print uniform_vec
		label_to_doc = {}
		
		for label in top_labels:
			label_to_doc[label] = set()


		docs_used = {}

		if normal:
			print 'used docs in reweighting: ' + str(len(pred_label))
			for doc, score in doc_score.iteritems():
				label_to_doc[pred_label[doc]].add(doc)
		else:
			for label in top_labels:
				p = label.lower()
				# idx = label_to_idx[label]
				for doc in pd_map[p]:
					label_to_doc[label].add(doc)
					if doc not in docs_used:
						docs_used[doc] = set()
					docs_used[doc].add(label)
			print 'docs used: %d' % len(docs_used)




		cnt_vec = [0.0] * len(top_labels)
		for label in label_to_doc:
			cnt_vec[label_to_idx[label]] = len(label_to_doc[label])
		comp_vec = utils.l1_normalize(cnt_vec)

		print cnt_vec

		# print comp_vec

		distinct_map = {}
		
		if normal:
			for phrase in embs[mid_type]:
				p_vec = [0.0] * len(top_labels)

				# if len(pd_map[phrase]) < 100:
				# 	continue

				for doc in pd_map[phrase]:
					idx = label_to_idx[pred_label[doc]]
					p_vec[idx] += 1.0
				
				if sum(p_vec) == 0:
					print 'ERROR!!!!!!!!!!'
					continue

				p_vec = utils.l1_normalize(p_vec)

				# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
				kl = utils.kl_divergence(p_vec, uniform_vec)
				# kl = utils.kl_divergence(p_vec, comp_vec)
				distinct_map[phrase] = kl
		else:
			for phrase in embs[mid_type]:
				p_vec = [0.0] * len(top_labels)

				# if len(pd_map[phrase]) < 100:
				# 	continue

				for doc in pd_map[phrase]:
					if doc in docs_used:
						for label in docs_used[doc]:
							idx = label_to_idx[label]
							p_vec[idx] += 1.0

				# print p_vec
				
				if sum(p_vec) == 0:
					distinct_map[phrase] = 0
					# print 'ERROR!!!!!!!!!!'
					continue
				
				# p_vec = [x / cnt_vec[i] for i, x in enumerate(p_vec)]


				p_vec = utils.l1_normalize(p_vec)

				# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
				# kl = utils.kl_divergence(p_vec, uniform_vec)
				kl = utils.kl_divergence(p_vec, comp_vec)
				distinct_map[phrase] = kl

		dist_map = distinct_map
		# with open('focal_comp.txt', 'w+') as g:
		# 	for (ph, score) in sorted(dist_map.items(), key=operator.itemgetter(1), reverse=True):
		# 		g.write('%s,%f\t' % (ph, score))

		# print '============= phrase distinctness computed.'

		agg_embs[source_type] = weighted_avg_embedding(dp_map, agg_embs[mid_type], dist_map, vec_size)
		# print '============= doc embedding aggregated.'

		print '*********** Aggregate with distinct at iter ' + str(i + 1)
		evaluate(agg_embs, true_file, target_dim)
	


def reweight_test(embs, dp_file):

	source_type = 'd'
	target_type = 'l'

	target_embs = embs[target_type]
	pred_label = {}
	doc_score = {}
	ratio = 1

	for doc in embs[source_type]:
		doc_emb = embs[source_type][doc]
		sim_map = classify_doc(doc_emb, target_embs)
		pred_label[doc] = hier.get_node(sim_map[0][0]).get_ascendant(1).path
		doc_score[doc] = sim_map[0][1]

	doc_score = sorted(doc_score.items(), key=operator.itemgetter(1), reverse=True)	
	filtered_docs = doc_score[:int(len(doc_score)*ratio)]

	top_labels = [w.path for w in hier.get_nodes_at_level(1)]

	# print meta stats
	top_label_cnts = {}
	for label in top_labels:
		top_label_cnts[label] = 0
	for doc_pair in filtered_docs:
		l = pred_label[doc_pair[0]]
		top_label_cnts[l] += 1
	print top_label_cnts
	print 'top level labels: ' + str(top_labels)
	# return

	label_to_idx = {}
	for idx, label in enumerate(top_labels):
		label_to_idx[label] = idx
	uniform_vec = [1.0/len(top_labels)] * len(top_labels)
	print uniform_vec
	label_to_doc = {}

	# new_filter = []
	# new_pred_ls = {}
	# for (doc, score) in filtered_docs:
	# 	if pred_label[doc] not in top_labels:
	# 		continue
	# 	new_filter.append((doc, score))
	# 	new_pred_ls[doc] = pred_label[doc]
	# filtered_docs = new_filter
	# pred_label = new_pred_ls

	pd_map = load_dp(dp_file, reverse=True)
	
	for label in top_labels:
		label_to_doc[label] = set()

	print 'used docs in reweighting: ' + str(len(filtered_docs))
	for (doc, score) in filtered_docs:
		label_to_doc[pred_label[doc]].add(doc)

	distinct_map = {}
	cnt = 0
	for phrase in embs['p']:
		p_vec = [0.0] * len(top_labels)

		if len(pd_map[phrase]) < 100:
			continue

		for doc in pd_map[phrase]:
			if doc not in pred_label:
				continue
			idx = label_to_idx[pred_label[doc]]
			p_vec[idx] += 1.0
		
		if sum(p_vec) == 0:
			continue

		p_vec = utils.l1_normalize(p_vec)

		kl = utils.kl_divergence(p_vec, uniform_vec)
		distinct_map[phrase] = kl

	distinct_map = sorted(distinct_map.items(), key=operator.itemgetter(1), reverse=False)
	print distinct_map[:100]
	print 
	print distinct_map[:-100]

def classify_doc_real(t_emb, target_embs, pmode):
	# if not hierarchical
	sim_map = {}
	for key in target_embs:
		if pmode == 'COS':
			sim_map[key] = utils.cossim(t_emb, target_embs[key])
		if pmode == 'DOT':
			sim_map[key] = utils.dot_product(t_emb, target_embs[key])
	sim_map = sorted(sim_map.items(), key=operator.itemgetter(1), reverse=True)
	return sim_map


def classify_doc(t_emb, target_embs):
	# if not hierarchical
	return classify_doc_real(t_emb, target_embs, pmode)

	# TODO: hierarchical classify

def eval_add_instance(label_map, target_embs, true_label, t_emb):
	# if mode == FLAT: then regard all nodes as the same
	# if mode == TOP: only evaluate the top level performance

	if emode == 'FLAT' or emode == 'TOP':
		sim_map = classify_doc(t_emb, target_embs)

		if emode == 'FLAT':	
			if sim_map[0][0] == true_label:
				label_map['all']['y_cnt'] += 1
				label_map[true_label]['y_cnt'] += 1
			else:
				label_map['all']['n_cnt'] += 1
				label_map[true_label]['n_cnt'] += 1
		if emode == 'TOP':
			top_true = hier.get_node(true_label).get_ascendant(1).path
			top_pred = hier.get_node(sim_map[0][0]).get_ascendant(1).path
			if top_true == top_pred:
				label_map['all']['y_cnt'] += 1
				label_map[top_true]['y_cnt'] += 1
			else:
				label_map['all']['n_cnt'] += 1
				label_map[top_true]['n_cnt'] += 1
	
	if emode == 'HIER':
		# TODO
		return
	
def print_label_map(label_map):
	for label in label_map:
		if label_map[label]['y_cnt'] + label_map[label]['n_cnt'] <= 0:
			continue
		mat_str = ': matched: ' + str(label_map[label]['y_cnt'])
		miss_str = '; missed: ' + str(label_map[label]['n_cnt'])
		prec_str = '; precision: ' + str(float(label_map[label]['y_cnt'])/(label_map[label]['n_cnt'] + label_map[label]['y_cnt']))
		print label + mat_str + miss_str + prec_str

def evaluate(embs, true_file, target_dim, mode='Emb'):
	# if mode=Emb, then use embedding for evaluation
	source_type = 'd'
	target_type = 'l'

	label_map = {'all': {'y_cnt': 0, 'n_cnt': 0}}
	y_cnt = 0
	n_cnt = 0

	if mode == 'Emb':
		ground_truth = {}
		target_embs = embs[target_type]
		source_embs = embs[source_type]
		
		for target in hier.all_nodes:
			label_map[target] = {'y_cnt':0, 'n_cnt': 0}

		with open(true_file, 'r') as f:
			for line in f:
				segs = line.strip('\r\n').split('\t')
				ground_truth[segs[0]] = segs[1 + target_dim]

		pred_labels = {}
		for doc in ground_truth:
			if doc not in source_embs:
				print 'doc ' + doc + ' is not in embedding'
			if ground_truth[doc] not in target_embs:
				print 'label ' + ground_truth[doc] + ' is not in embedding'
			s_emb = source_embs[doc]
		
			sim_map = classify_doc(s_emb, target_embs)
			pred_labels[doc] = sim_map[0][0]

			# eval_add_instance(label_map, target_embs, 
			# 	ground_truth[doc], s_emb)

		# y_cnt = label_map['all']['y_cnt']
		# n_cnt = label_map['all']['n_cnt']
		# print 'matched: ' + str(y_cnt)
		# print 'missed: ' + str(n_cnt)
		# print 'precision: ' + str(float(y_cnt)/(n_cnt + y_cnt))

		# temp
		accuracy(ground_truth, pred_labels)
		# macro_f1(ground_truth, pred_labels)

	else:
		pass
	# print_label_map(label_map)

def accuracy(ground_truth, pred_labels):
	y_cnt = 0
	n_cnt = 0
	for d in pred_labels:
		pred_l = pred_labels[d]
		if d not in ground_truth:
			continue
		g_l = ground_truth[d]
		if pred_l == g_l:
			y_cnt += 1
		else:
			n_cnt += 1
	# print 'matched: ' + str(y_cnt)
	# print 'missed: ' + str(n_cnt)
	precision = float(y_cnt)/(n_cnt + y_cnt)
	print 'accuracy: ' + str(precision)

	return precision


def macro_f1(ground_truth, pred_labels):
	labels = set()
	f1 = 0.0
	for d in ground_truth:
		labels.add(ground_truth[d])

	precs = {}
	recalls = {}

	stats = {l:{'tp':0, 'tp+fp':0, 'tp+fn':0} for l in labels} 
	# print stats

	for d in pred_labels:
		pred_l = pred_labels[d]
		if d not in ground_truth:
			continue
		g_l = ground_truth[d]
		stats[pred_l]['tp+fp'] += 1
		stats[g_l]['tp+fn'] += 1
		if pred_l == g_l:
			stats[pred_l]['tp'] += 1

	for l in labels:
		if stats[l]['tp+fp'] > 0:
			precs[l] = float(stats[l]['tp']) / stats[l]['tp+fp']
		else:
			precs[l] = 0
		if stats[l]['tp+fn'] > 0:
			recalls[l] = float(stats[l]['tp']) / stats[l]['tp+fn']
		else:
			recalls[l] = 0

	# bad_cates = ['Business|Stocks_and_Bonds', 'Business|Stocks']
	bad_cates = []

	for cate in bad_cates:
		precs.pop(cate, None)
		recalls.pop(cate, None)

	prec_sum = sum([precs[x] for x in precs])
	macro_prec = prec_sum / len(labels)

	rec_sum = sum([recalls[x] for x in recalls])
	macro_rec = rec_sum / len(labels)

	f1 = 2 * macro_prec * macro_rec / (macro_prec + macro_rec)

	print 'macro f1: %f' % f1
	return f1


def evaluate_baseline(true_file, pred_file, target_dim):
	ground_truth = {}
	pred_labels = {}

	with open(true_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			ground_truth[segs[0]] = segs[1 + target_dim]
	with open(pred_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			pred_labels[segs[0]] = segs[1]

	accuracy(ground_truth, pred_labels)
	macro_f1(ground_truth, pred_labels)


if __name__ == "__main__":

	import time
	start = time.time()

	parser = argparse.ArgumentParser(prog='evaluate.py', \
		description='Evaluating result.')
	parser.add_argument('-fmode', required=True, \
		help='The mode of evaluate.py')
	parser.add_argument('-emode', required=False, \
		help='evaluation computation mode')
	parser.add_argument('-pmode', required=False, \
		help='evaluation proximity mode')
	parser.add_argument('-eval', required=False, \
		help='eval file')
	parser.add_argument('-folder', required=False, \
		help='data folder')

	args = parser.parse_args()
	if args.pmode is not None:
		pmode = args.pmode
	else:
		pmode = 'COS'
	if args.emode is not None:
		emode = args.emode
	else:
		emode = 'FLAT'

	print args


	folder = args.folder
	true_file = args.eval
	# true_file = '../data_news/dl_balance.txt'
	l_prel_file = args.folder + 'l_prel.txt'
	dp_file = args.folder + 'dp.txt'
	lp_file = args.folder + 'lp.txt'

	e_size, embs = load_embedding(folder)
	hier = Hierarchy(l_prel_file)
	

	if args.fmode == 'eval':
		evaluate(embs, true_file, target_dim)

	if args.fmode == 'distance':
		distance_q('p', 'l', embs, e_size)

	if args.fmode == 'reweight':
		reweight(embs, dp_file, lp_file)
		# reweight_test(embs, dp_file)

	if args.fmode == 'expan':
		expan(embs, l_prel_file, dp_file, lp_file, mode='DIS')
		# expan(embs, l_prel_file, dp_file, lp_file, mode='EMB')

	if args.fmode == 'baseline':
		# pred_file = '../data_news/baseline_output/count.txt'
		# print 'Count Baseline'
		# evaluate_baseline(true_file, pred_file, target_dim)
		print 'Para2vec Baseline'
		pred_file = '../data_news/baseline_output/paragraph2vec.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'Word2vec Baseline'
		pred_file = '../data_news/baseline_output/word2vec.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'Word2vec + Concentration Baseline'
		pred_file = '../data_news/baseline_output/word2vec_cen.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'TFIDF Baseline'
		pred_file = '../data_news/baseline_output/ir.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'TFIDF + Query Expansion Baseline'
		pred_file = '../data_news/baseline_output/ir_qe.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'Topic Modeling'
		pred_file = '../data_news/baseline_output/tm.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'Topic Modeling with Prior'
		pred_file = '../data_news/baseline_output/tmwp'
		evaluate_baseline(true_file, pred_file, target_dim)
		print 'Dataless'
		pred_file = '../data_news/baseline_output/dataless_n.txt'
		evaluate_baseline(true_file, pred_file, target_dim)
