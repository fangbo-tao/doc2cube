from read_files import *
import operator
import sys
import math
from label_hierarchy import Hierarchy
from evaluate import classify_doc_real, doc_assignment, weighted_avg_embedding
sys.path.append('../../')
from cube_construction import utils

simple_stop = set(['and', 'the', 'to', '&'])
hier = None

def count_baseline(net, o_file):
	null_cnt = 0
	d_l_preds = {}

	for d in net.ds:
		l_count = {}
		for link in net.dp[d]:
			if link.v in net.seeds:
				l = net.seeds[link.v]
				if l not in l_count:
					l_count[l] = 0
				l_count[l] += link.w
		if len(l_count) == 0:
			null_cnt += 1
			d_l_preds[d] = 'null'
		else:
			l_count = sorted(l_count.items(), key=operator.itemgetter(1), reverse=True)
			# print l_count
			pred_l = l_count[0][0]
			d_l_preds[d] = pred_l

	print 'Num of Unclassified Doc: ' + str(null_cnt) 

	with open(o_file, 'w+') as g:
		for d in d_l_preds:
			g.write(d + '\t' + d_l_preds[d] + '\n')


def topic_model_baseline(net, doc_topic_f, did_map_f, tm_l_f, o_file):
	# Run topic modeling, and then manually assign topics to categories
	d_map = {}
	with open(did_map_f) as f:
		for line in f:
			o_did, n_did = line.strip('\r\n').split('\t')
			d_map[o_did] = n_did

	tm_l_map = {}
	with open(tm_l_f) as f:
		for line in f:
			tm_id, l_name = line.strip('\r\n').split('\t')
			tm_l_map[int(tm_id)] = l_name

	d_l_preds = {}
	with open(doc_topic_f) as f:
		for line in f:
			segments = line.strip('\r\n').split('\t')
			o_did = segments[1].split('/')[-1]
			if o_did not in d_map:
				continue
			n_did = d_map[o_did]
			tm_vec = [float(x) for x in segments[2:]]
			tm_id = tm_vec.index(max(tm_vec))
			l_name = tm_l_map[tm_id]
			d_l_preds[n_did] = l_name
			if o_did == '1':
				print n_did
				print tm_vec
				print tm_id
				print l_name
				

	
	with open(o_file, 'w+') as g:
		for d in d_l_preds:
			g.write(d + '\t' + d_l_preds[d] + '\n')	


def get_idf(net, idf_map):

	# remove stop words
	# idf_map.pop('the', None)
	# idf_map.pop('and', None)

	d_cnt = len(net.ds)
	pd_map = net.get_pd()

	d_token_map = {}
	for d in net.ds:
		d_token_map[d] = {}
		for t in idf_map:
			d_token_map[d][t] = 0

	for p in net.ps:
		tokens = p.lower().split('_')
		for token in tokens:
			if token in idf_map:
				# compute documents
				for d_link in pd_map[p]:
					token_cnt = int(math.exp(d_link.w - 1) - 1)
					idf_map[token].add(d_link.v)
					d_token_map[d_link.v][token] += token_cnt
	# for d in net.ds:
	# 	for t in idf_map:
	# 		d_token_map[d][t] = 
	
	# sss = {x:len(idf_map[x]) for x in idf_map}
	# print sss

	for t in idf_map:
		if len(idf_map[t]) == 0:
			idf_map[t] = math.log(100)
		else:
			idf_map[t] = math.log(float(d_cnt) / len(idf_map[t]))

	# print idf_map

	return idf_map, d_token_map
	

def ir_baseline(net, o_file):
	# TF-IDF to the query used
	scores = {}
	l_tokens = {}
	idf_map = {}
	d_l_preds = {}

	for l in net.ls:
		tokens = l.split('|')[-1].lower().split('_')
		tokens = [x for x in tokens if x not in simple_stop]
		l_tokens[l] = tokens
		for t in tokens:
			idf_map[t] = set()

	idf_map, d_token_map = get_idf(net, idf_map)

	for d in net.ds:
		scores[d] = {}
		for l in net.ls:
			scores[d][l] = 0
			for token in l_tokens[l]:
				tf = d_token_map[d][token]
				idf = idf_map[token]
				scores[d][l] += tf * idf
		d_l_preds[d] = sorted(scores[d].items(), key=operator.itemgetter(1), reverse=True)[0][0]

	with open(o_file, 'w+') as g:
		for d in d_l_preds:
			g.write(d + '\t' + d_l_preds[d] + '\n')	

	return

def ir_qe_baseline(net, emb_file, o_file, expan_lim=5):
	# IR + query expansion, emb_file is the word2vec document
	scores = {}
	l_tokens = {}
	idf_map = {}
	d_l_preds = {}

	# expand using word2vec
	l_expan = {}
	e_size, embs = load_word2vec(emb_file)
	for l in net.ls:
		label_txt = l.split('|')[-1].lower()
		sim_map = {}
		for p in embs:
			sim_map[p] = utils.cossim(embs[label_txt], embs[p])
		top_expan = sorted(sim_map.items(), key=operator.itemgetter(1), reverse=True)[:expan_lim]
		top_expan = [x[0] for x in top_expan]
		l_expan[l] = top_expan

	print l_expan

	for l in net.ls:
		l_tokens[l] = set()
		for phrase in l_expan[l]:
			tokens = phrase.split('|')[-1].lower().split('_')
			tokens = [x for x in tokens if x not in simple_stop]
			for t in tokens:
				l_tokens[l].add(t)
				idf_map[t] = set()

	idf_map, d_token_map = get_idf(net, idf_map)

	for d in net.ds:
		scores[d] = {}
		for l in net.ls:
			scores[d][l] = 0
			for token in l_tokens[l]:
				tf = d_token_map[d][token]
				idf = idf_map[token]
				scores[d][l] += tf * idf
		d_l_preds[d] = sorted(scores[d].items(), key=operator.itemgetter(1), reverse=True)[0][0]

	with open(o_file, 'w+') as g:
		for d in d_l_preds:
			g.write(d + '\t' + d_l_preds[d] + '\n')	

	return


def word2vec_baseline(net, emb_file, o_file):
	e_size, embs = load_word2vec(emb_file)
	d_embs = {}
	l_embs = {}

	for d in net.ds:
		ele_map = {}
		for link in net.dp[d]:
			if link.v not in embs:
				# print 'ERROR!! ' + link.v
				pass
			else:
				ele_map[link.v] = link.w

			# print ele_map

		d_embs[d] = utils.avg_emb(ele_map, embs, e_size)

	for l in net.ls:
		ele_map = {}
		for link in net.lp[l]:
			if link.v not in embs:
				print 'ERROR!! ' + link.v
			else:
				ele_map[link.v] = link.w
		# print ele_map

		l_embs[l] = utils.avg_emb(ele_map, embs, e_size)

	# classify
	with open(o_file, 'w+') as g:
		for d in net.ds:
			sim_map = classify_doc_real(d_embs[d], l_embs, 'DOT')
			g.write(d + '\t' + sim_map[0][0] + '\n')


def word2vec_concentration_baseline(net, emb_file, o_file):
	e_size, embs = load_word2vec(emb_file)
	d_embs = {}
	l_embs = {}

	for d in net.ds:
		ele_map = {}
		for link in net.dp[d]:
			if link.v not in embs:
				# print 'ERROR!! ' + link.v
				embs[link.v] = embs['news']
				pass
			else:
				ele_map[link.v] = link.w

			# print ele_map

		d_embs[d] = utils.avg_emb(ele_map, embs, e_size)

	for l in net.ls:
		ele_map = {}
		for link in net.lp[l]:
			if link.v not in embs:
				print 'ERROR!! ' + link.v
			else:
				ele_map[link.v] = link.w
		# print ele_map

		l_embs[l] = utils.avg_emb(ele_map, embs, e_size)


	agg_embs = {'d':d_embs, 'l':l_embs, 'p':embs}
	dp_map = net.simple_dp_map()

	dist_map = {x:1.0 for x in embs}
	pd_map = net.get_pd()
	top_labels = [w.path for w in hier.get_nodes_at_level(1)]
	label_to_idx = {}
	for idx, label in enumerate(top_labels):
		label_to_idx[label] = idx
	uniform_vec = [1.0/len(top_labels)] * len(top_labels)

	for i in range(1):
		# pred_label, doc_score = doc_assignment(agg_embs, 'd', 'l', hierr=hier)
		pred_label = {}
		doc_score = {}
		ratio = 1

		normal = False

		for doc in agg_embs['d']:
			doc_emb = agg_embs['d'][doc]
			sim_map = classify_doc_real(doc_emb, agg_embs['l'], 'DOT')
			pred_label[doc] = hier.get_node(sim_map[0][0]).get_ascendant(1).path
			doc_score[doc] = sim_map[0][1]
		
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
				for link in pd_map[p]:
					doc = link.v
					label_to_doc[label].add(doc)
					if doc not in docs_used:
						docs_used[doc] = set()
					docs_used[doc].add(label)
			print 'docs used: %d' % len(docs_used)

		# temp
		new_uni_vec = [0.0] * len(top_labels)
		for label in label_to_idx:
			new_uni_vec[label_to_idx[label]] = float(len(label_to_doc[label]))
		print new_uni_vec
		new_uni_vec = utils.l1_normalize(new_uni_vec)

		if normal: 
			for phrase in embs:
				if phrase not in pd_map:
					continue

				p_vec = [0.0] * len(top_labels)

				for link in pd_map[phrase]:
					doc = link.v
					idx = label_to_idx[pred_label[doc]]
					p_vec[idx] += 1.0
				
				if sum(p_vec) == 0:
					print 'ERROR!!!!!!!!!!'
					continue

				p_vec = utils.l1_normalize(p_vec)

				# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
				# kl = utils.kl_divergence(p_vec, uniform_vec)
				
				# temp
				kl = utils.kl_divergence(p_vec, new_uni_vec)
				
				dist_map[phrase] = kl
		else:
			for phrase in embs:
				if phrase not in pd_map:
					continue

				p_vec = [0.0] * len(top_labels)

				# if len(pd_map[phrase]) < 100:
				# 	continue

				for link in pd_map[phrase]:
					doc = link.v
					if doc in docs_used:
						for label in docs_used[doc]:
							idx = label_to_idx[label]
							p_vec[idx] += 1.0

				# print p_vec
				
				if sum(p_vec) == 0:
					dist_map[phrase] = 0
					# print 'ERROR!!!!!!!!!!'
					continue
				
				# p_vec = [x / cnt_vec[i] for i, x in enumerate(p_vec)]


				p_vec = utils.l1_normalize(p_vec)

				# kl = 0.1 + 0.9 * utils.kl_divergence(p_vec, uniform_vec)
				# kl = utils.kl_divergence(p_vec, uniform_vec)
				kl = utils.kl_divergence(p_vec, new_uni_vec)
				dist_map[phrase] = kl

		agg_embs['d'] = weighted_avg_embedding(dp_map, agg_embs['p'], dist_map, e_size)
		print '%d iteration done.' % (i + 1)


	# classify
	with open(o_file, 'w+') as g:
		for d in net.ds:
			sim_map = classify_doc_real(agg_embs['d'][d], l_embs, 'DOT')
			g.write(d + '\t' + sim_map[0][0] + '\n')





if __name__ == "__main__":
	folder = '../data_news/'
	# net = read_network(
	# 	folder + 'd.txt',
	# 	folder + 'p.txt',
	# 	folder + 'l_topic.txt',
	# 	folder + 'lp_topic.txt',
	# 	folder + 'dp.txt')
	
	# l_prel_file = '../data_news/l_prel_topic.txt'
	# hier = Hierarchy(l_prel_file)

	# o_folder = folder + 'baseline_output/'
	# count_baseline(net, o_folder + 'count.txt')
	# word2vec_baseline(net, folder + 'vectors.txt', o_folder + 'word2vec.txt')
	# word2vec_concentration_baseline(net, folder + 'vectors.txt', o_folder + 'word2vec_cen.txt')
	# ir_baseline(net, o_folder + 'ir.txt')
	# ir_qe_baseline(net, folder + 'vectors.txt', o_folder + 'ir_qe.txt')

	# topic_model_baseline(net, folder + 'doc_topic.txt',
	# 	folder + 'd40000to10000_mapping.txt', 
	# 	folder + 'tm_topic_mapping.txt', o_folder + 'tm.txt')



	# net = read_network(
	# 	folder + 'd.txt',
	# 	folder + 'p.txt',
	# 	folder + 'l_loc.txt',
	# 	folder + 'lp_loc.txt',
	# 	folder + 'dp.txt')
	
	# l_prel_file = '../data_news/l_prel_loc.txt'
	# hier = Hierarchy(l_prel_file)

	# o_folder = folder + 'baseline_output_loc/'
	# # count_baseline(net, o_folder + 'count.txt')
	# # word2vec_baseline(net, folder + 'vectors.txt', o_folder + 'word2vec.txt')
	# word2vec_concentration_baseline(net, folder + 'vectors.txt', o_folder + 'word2vec_cen.txt')
	# # ir_baseline(net, o_folder + 'ir.txt')
	# # ir_qe_baseline(net, folder + 'vectors.txt', o_folder + 'ir_qe.txt')

	# topic_model_baseline(net, folder + 'doc_topic.txt',
	# 	folder + 'd40000to10000_mapping.txt', 
	# 	folder + 'tm_loc_mapping.txt', o_folder + 'tm.txt')


	folder = '../data_pubmed/'

	for dim in ['2']:
		net = read_network(
			folder + 'd.txt',
			folder + 'p.txt',
			folder + 'l_' + dim + '.txt',
			folder + 'lp_' + dim + '.txt',
			folder + 'dp.txt')
		
		l_prel_file = '../data_pubmed/l_prel_' + dim + '.txt'
		hier = Hierarchy(l_prel_file)

		o_folder = folder + 'baseline_output_' + dim + '/'
		# count_baseline(net, o_folder + 'count.txt')
		word2vec_baseline(net, folder + 'vectors.txt', o_folder + 'word2vec.txt')
		word2vec_concentration_baseline(net, folder + 'vectors.txt', o_folder + 'word2vec_cen.txt')
		ir_baseline(net, o_folder + 'ir.txt')
		ir_qe_baseline(net, folder + 'vectors.txt', o_folder + 'ir_qe.txt')



