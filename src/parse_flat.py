import sys
import math
import argparse
import preprocess
from label_hierarchy import Hierarchy

# This file handles the simplified case where only meta data and text data are 


def build_graph(dl_file, d_file, l_file, p_file, 
	dp_file, lp_file, pte_d, pte_l, l_mapping, p_thre=10):
	# Build L-D-P graph using dl and d files
	# s_file: seed file
	
	all_tokens = {}	# key token name, value: id
	all_token_cnt = {}
	doc_token_map = {}

	# tokenize
	print 'tokenizing...\n'
	texts = []
	dids = []
	ls = []
	with open(d_file, 'r') as f:
		token_id = 0
		for line in f:
			segs = line.strip('\r\n').split('\t')
			did = segs[0]
			dids.append(did)
			doc_token_map[did] = {}
			tokens = segs[1].split(';')
			for token in tokens:
				if token == '':
					continue
				if token not in all_tokens:
					all_tokens[token] = token_id
					all_token_cnt[token] = 0
					token_id += 1
				if token not in doc_token_map[did]:
					doc_token_map[did][token] = 0
				doc_token_map[did][token] += 1
				all_token_cnt[token] += 1

	label_tokens = set()
	with open(l_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			if len(segs[2]) > 0:
				label_tokens.add(segs[2].lower())

	# filter tokens by frequency
	valid_tokens = set()
	for token in all_token_cnt:
		if all_token_cnt[token] >= p_thre:
			valid_tokens.add(token)
		if token in label_tokens:
			valid_tokens.add(token)

	all_tokens = {}
	doc_token_map = {}
	with open(d_file, 'r') as f:
		token_id = 0
		for line in f:
			segs = line.strip('\r\n').split('\t')
			did = segs[0]
			doc_token_map[did] = {}
			tokens = segs[1].split(';')
			for token in tokens:
				# skip
				if token not in valid_tokens:
					continue
				if token not in all_tokens:
					all_tokens[token] = token_id
					all_token_cnt[token] = 0
					token_id += 1
				if token not in doc_token_map[did]:
					doc_token_map[did][token] = 0
				doc_token_map[did][token] += 1
				all_token_cnt[token] += 1


	# log weighting
	for did in doc_token_map:
		for token in doc_token_map[did]:
			doc_token_map[did][token] = 1 + math.log(1 + doc_token_map[did][token])

	# check seeds
	print 'linking seeds to labels...\n'
	lp_f = open(lp_file, 'w+')
	with open(l_file, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			lid = segs[0]
			if segs[1] == '*':
				continue

			ls.append(segs[1])
			seeds = [w.lower() for w in segs[2].split('|')]
			for seed in seeds:
				if seed in all_tokens:
					print seed + ' in tokens'
					tid = all_tokens[seed]
					# for pte format
					# lp_f.write(lid + '\t' + str(tid) + '\n')
					lp_f.write(segs[1] + '\t' + seed + '\t1\n')
				else:
					print seed + ' not in tokens'
	lp_f.close()


	print 'linking phrases to docs...'
	with open(p_file, 'w+') as g:
		for token in all_tokens:
			# for pte format
			# line = str(all_tokens[token]) + '\t' + token + '\n'
			line = token + '\t' + '0' + '\n'

			g.write(line)

	with open(dp_file, 'w+') as g:
		for did in doc_token_map:
			for token in doc_token_map[did]:
				tid = all_tokens[token]
				weight = doc_token_map[did][token]
				# for pte format
				# line = str(did) + '\t' + str(tid) + '\t' + str(weight) + '\n'
				line = str(did) + '\t' + token + '\t' + str(weight) + '\n'

				g.write(line)


	# for pte format
	# re-save d.txt
	with open(pte_d, 'w+') as g:
		for did in dids:
			g.write(did + '\t' + '0\n')
	# re-save l.txt
	with open(pte_l, 'w+') as g:
		for label in ls:
			if label == '*':
				continue
			g.write(label + '\t' + '0\n')

	hier = Hierarchy(l_file)
	with open(l_mapping, 'w+') as g:
		for key, value in hier.all_nodes.iteritems():
			if key == '*':
				continue
			top_path = value.get_ascendant(1).path
			g.write(value.path + '\t' + top_path + '\n')

	print 'network constructed'



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='.')
	parser.add_argument('-text', help='')
	parser.add_argument('-folder', help='')
	args = parser.parse_args()

	folder = args.folder
	build_graph(args.text, folder + 'd_prel.txt', folder + 'l_prel.txt', 
		folder + 'p.txt', folder + 'dp.txt', folder + 'lp.txt', 
		folder + 'd.txt', folder + 'l.txt', folder + 'l_mapping.txt')


