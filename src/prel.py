import nltk
import string
import argparse


parser = argparse.ArgumentParser(description='.')
parser.add_argument('-text', help='')
parser.add_argument('-meta', help='')
parser.add_argument('-output', help='')
args = parser.parse_args()

# parser.add_argument('-iter', dest='iter', type=int,
#                     default=max_iter)


text_docs = {}

with open(args.text, 'r') as f:
	with open(args.output + 'd_prel.txt', 'w+') as g:
		idx = 0
		for line in f:
			tokens = [w.lower().replace('###', '_') for w in line.strip('\r\n').split(' ')]
			stopwords = nltk.corpus.stopwords.words('english')
			tokens = [w for w in tokens if w not in stopwords]
			line = str(idx) + '\t' + ';'.join(tokens) + ';\n'
			g.write(line)
			idx += 1


with open(args.output + 'l_prel.txt', 'w+') as g:
	g.write('0	*	\n')
	with open(args.meta, 'r') as f:
		idx = 0
		for line in f:
			idx += 1
			path = line.strip('\r\n')
			value = path.split('|')[-1]
			g.write(str(idx) + '\t' + path + '\t' + value + '\n')


# prel => parse_flat => run.sh
# ==> evaluate.py