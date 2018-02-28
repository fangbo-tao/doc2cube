import sys
import math
sys.path.append('../../')
from cube_construction import preprocess
from label_hierarchy import Hierarchy


def find_joint_docs(folder):
	contained_docs = {}
	joint_docs = {}


	with open(folder + '/doc_map.txt', 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			contained_docs[segs[0]] = segs[1]

	with open(folder + '/doc_topic_map_for_construction.txt', 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			if segs[0] in contained_docs:
				new_id = contained_docs[segs[0]]
				topic = segs[1]
				joint_docs[new_id] = topic

	return joint_docs

def create_data_file(joint_docs, loc_docs, dl_file, 
		doc_file, new_doc_file, label_file_prefix, loc_list=None):
	# create data file in step 1
	new_index = 0

	docs = {}
	with open(doc_file, 'r') as f:
		idx = 0
		for line in f:
			docs[idx] = line.strip('\r\n')
			idx += 1

	# print 'doc length'
	# print len(docs)

	doc_g = open(new_doc_file, 'w+')
	# g_doc_id_mapping = open('../data_news/d_mapping.txt', 'w+')
	topics = set()
	locs = set()

	with open(dl_file, 'w+') as g:
		for loc in loc_list:
			for aid in loc_docs[loc]:
				# print new_index
				topic = joint_docs[aid].replace('=>', '|')[:-1].replace(' ', '_')
				doc = docs[int(aid)]
				

				parsed_loc = loc[9:-1]
				# if 'China' in loc:
				# 	print loc
				# 	print parsed_loc
				topics.add(topic)
				locs.add(parsed_loc)

				line = str(new_index) + '\t' + topic + '\t' + parsed_loc + '\n'
				g.write(line)

				# g_doc_id_mapping.write('%d\t%d\n' % (int(aid), new_index))

				# with open(linked_doc_folder + aid, 'r') as myfile:
				# 	linked_doc =myfile.read().replace('\n', '')

				# tokens = preprocess.parse_one_doc(docs[int(aid)])
				tokens = [w.lower().replace('###', '_') for w in docs[int(aid)].split(' ')]
				doc_tokens = ';'.join(tokens)
				doc_g.write(str(new_index) + '\t' + doc_tokens + '\n')
				
				new_index += 1

	doc_g.close()
	# g_doc_id_mapping.close()

	idx = 0
	with open(label_file_prefix + '_topic.txt', 'w+') as f:
		f.write('0\t*\t\n')
		for item in topics:
			idx += 1
			item = item.replace(' ', '_')
			f.write(str(idx) + '\t' + item + '\t' + get_last_label(item) + '\n')

	print len(locs)
	idx = 0
	with open(label_file_prefix + '_loc.txt', 'w+') as f:
		f.write('0\t*\n')
		for item in locs:
			idx += 1
			item = item.replace(' ', '_')
			f.write(str(idx) + '\t' + item + '\t' + get_last_label(item) + '\n')


def get_last_label(label):
	if '|' not in label:
		return label

	return label.split('|')[-1]


def convert_segphrase(doc_file, doc_file_new):
	n_doc_f = open(doc_file_new, 'w+')

	with open(doc_file, 'r') as f:
		for line in f:
			n_line = ''
			in_phrase = False
			current_word = ''
			for char in line:
				if char == '[':
					in_phrase = True
				elif char == ']':
					in_phrase = False
					n_line += current_word + ' '
					current_word = ''
				else:
					if in_phrase:
						if char == ' ':
							current_word += '###'
						else:
							current_word += char
			n_doc_f.write(n_line + '\n')

	n_doc_f.close()

def convert_for_word2vec(doc_file, doc_file_new):
	n_doc_f = open(doc_file_new, 'w+')

	with open(doc_file, 'r') as f:
		for line in f:
			n_line = ''
			in_phrase = False
			current_word = ''
			for char in line:
				if char == '[':
					in_phrase = True
				elif char == ']':
					in_phrase = False
					n_line += current_word + ' '
					current_word = ''
				else:
					if in_phrase:
						if char == ' ':
							current_word += '###'
						else:
							current_word += char
					else:
						if char == ' ':
							if len(current_word) > 0:
								n_line += current_word + ' '
								current_word = ''
						
						elif char == '"' or char == ':' or char == '\'':
							pass
						else:
							current_word += char

			n_line = n_line.replace('.', '. ').replace('  ', ' ').lower()
			n_doc_f.write(n_line + '\n')

	n_doc_f.close()



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

	# filter tokens by frequency
	valid_tokens = set()
	for token in all_token_cnt:
		if all_token_cnt[token] >= p_thre:
			valid_tokens.add(token)
		if token == 'federal_budget' or token == 'international_business':
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


# convert_segphrase('used/docs_50000.txt', 'used/docs_parsed.txt')
# convert_for_word2vec('used/docs_50000.txt', 'used/docs_word2vec.txt')
# print len(joint_docs)
if __name__ == "__main__":
	folder = '../data_news/'
	# convert_for_word2vec(folder + 'used/docs_50000.txt', folder + 'used/docs_word2vec.txt')
	# build_graph(folder + 'dl.txt', folder + 'd_prel.txt', folder + 'l_prel_topic.txt', folder + 'p.txt', 
	# 	folder + 'dp.txt', folder + 'lp_topic.txt', folder + 'd.txt', folder + 'l_topic.txt', folder + 'l_topic_mapping.txt')
	build_graph(folder + 'dl.txt', folder + 'd_prel.txt', folder + 'l_prel_loc.txt', 
		folder + 'p.txt', folder + 'dp.txt', folder + 'lp_loc.txt', 
		folder + 'd.txt', folder + 'l_loc.txt', folder + 'l_loc_mapping.txt')

