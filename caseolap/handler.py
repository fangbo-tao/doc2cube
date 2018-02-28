from caseslim import CaseSlim
import ipdb

group_name = "Economies" #"Economies", "Countries", "Topics"
file_phrase = '../data/caseolap/' + group_name + '_phrase.txt'
file_cell = '../data/caseolap/' + group_name + '_cell.txt'

file_out = open('../data/caseolap/' + group_name + '_result.txt', 'w+')


cells = {}
freq_data = {}

with open(file_cell, 'r+') as f:
	for line in f:
		segments = line.strip('\n\r').split('\t')
		cell = segments[1]
		doc_id = segments[0]
		if cell not in cells:
			cells[cell] = []
		cells[cell].append(doc_id)

with open(file_phrase, 'r+') as f:
	for line in f:
		print 'sss' + line
		segments = line.strip('\n\r ').split(' ')
		doc_id = segments[0]
		freq_data[doc_id] = {}
		for phrase_count in segments[1:]:
			parts = phrase_count.split('|')
			print parts
			phrase = parts[0]
			count = int(parts[1])
			freq_data[doc_id][phrase] = count

# ipdb.set_trace()
all_context_group = {'all':[]}
for cell in cells:
	all_context_group['all'].extend(cells[cell])


for cell in cells:
	print 'Cell: %s' % cell
	selected_docs = cells[cell]
	context_doc_groups = {}
	for cell_2 in cells:
		if cell_2 != cell:
			context_doc_groups[cell_2] = cells[cell_2]
	# caseslim = CaseSlim(freq_data, selected_docs, context_doc_groups)
	caseslim = CaseSlim(freq_data, selected_docs, all_context_group)
	top_phrases = caseslim.compute()
	phr_str = ' '.join([ph[0] + '|' + str(ph[1]) for ph in top_phrases])
	file_out.write(str(cell) + '\t' + phr_str + '\n')

	print top_phrases[:20]
	print '\n'


file_out.close()