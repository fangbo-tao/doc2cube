import os

group_name = "Topics" #"Economies", "Countries", "Topics"
input_file = '../data/' + group_name + '.data'
output_file_phrase = '../data/caseolap/' + group_name + '_phrase.txt'
output_file_cell = '../data/caseolap/' + group_name + '_cell.txt'
splitter = "\t@@\t"

if not os.path.isfile(input_file):
    print 'Error: The input file does not exist.'
    exit(1)

g_phrase = open(output_file_phrase, 'w+')
g_cell = open(output_file_cell, 'w+')


doc_id = 0

with open(input_file, "r") as f:
	for line in f:
		doc_id += 1
		segments = line.split(splitter)
		text = segments[1]
		cell = segments[0]
		g_cell.write(str(doc_id) + '\t' + cell + '\n')
		tokens = text.split(' ')
		phrase_map = {}
		for token in tokens:
			if '###' in token:
				simp_token = token.strip(' \r\n.,?!~)(').lower().replace('###', '_')
				if simp_token in phrase_map:
					phrase_map[simp_token] += 1
				else:
					phrase_map[simp_token] = 1
		g_phrase.write(str(doc_id) + ' ')
		phrase_strs = []
		for phrase in phrase_map:
			phrase_strs.append(phrase + '|' + str(phrase_map[phrase]))
		g_phrase.write(' '.join(phrase_strs) + '\n')

g_phrase.close()
g_cell.close()

