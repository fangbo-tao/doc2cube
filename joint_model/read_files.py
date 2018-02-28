ntypes = ['d', 'l', 'p']

class Link:

	def __init__(self, u, v, w):
		self.u = u
		self.v = v
		self.w = float(w)

class LDPNet:

	def __init__(self):
		self.ds = set()
		self.ps = set()
		self.ls = set()
		self.dp = {}
		self.lp = {}
		self.seeds = {}

	def get_pd(self):
		self.pd = {}
		for p in self.ps:
			self.pd[p] = []
		for d in self.ds:
			for link in self.dp[d]:
				r_link = Link(link.v, link.u, link.w)
				self.pd[link.v].append(r_link)
		return self.pd

	def simple_dp_map(self):
		dp_map = {}
		for d in self.dp:
			dp_map[d] = {}
			for link in self.dp[d]:
				dp_map[d][link.v] = link.w
		return dp_map


def load_embedding(folder):

	embs = {}
	e_size = 0

	for n_type in ntypes:
		embs[n_type] = {}
		e_file = folder + n_type + '.vec'
		e_cnt = 0
		with open(e_file, 'r') as f:
			first_line = True
			for line in f:
				if first_line:
					e_cnt, e_size = [int(w) for w in line.strip('\r\n').split(' ')]
					first_line = False
					continue
				segs = line.strip('\r\n').split(' ')
				n_name = segs[0]
				n_emb = [float(w) for w in segs[1:-1]]
				if len(n_emb) != e_size:
					print 'Dimension length mismatch: ' + str(len(n_emb))
					exit(1)
				embs[n_type][n_name] = n_emb

	return e_size, embs

def load_word2vec(e_file):

	embs = {}
	e_size = 0
	with open(e_file, 'r') as f:
		first_line = True
		for line in f:
			if first_line:
				e_cnt, e_size = [int(w) for w in line.strip('\r\n').split(' ')]
				first_line = False
				continue
			segs = line.strip('\r\n').split(' ')
			n_name = segs[0].replace('###', '_')
			n_emb = [float(w) for w in segs[1:-1]]
			if len(n_emb) != e_size:
				print 'Dimension length mismatch: ' + str(len(n_emb))
				exit(1)
			embs[n_name] = n_emb

	return e_size, embs



def read_network(d_file, p_file, l_file, lp_file, dp_file):
	print 'start loading network'

	net = LDPNet()

	with open(d_file) as f:
		for line in f:
			node = line.split('\t')[0]
			net.ds.add(node)
	with open(l_file) as f:
		for line in f:
			node = line.split('\t')[0]
			net.ls.add(node)
	with open(p_file) as f:
		for line in f:
			node = line.split('\t')[0]
			net.ps.add(node)

	with open(dp_file) as f:
		for line in f:
			u, v, w = line.strip('\r\n').split('\t')
			link = Link(u, v, w)
			if u not in net.dp:
				net.dp[u] = []
			net.dp[u].append(link)
	with open(lp_file) as f:
		for line in f:
			u, v, w = line.strip('\r\n').split('\t')
			link = Link(u, v, w)
			if u not in net.lp:
				net.lp[u] = []
			net.lp[u].append(link)
			if v in net.seeds:
				if u != net.seeds[v]:
					print 'phrase ' + v + ' is seed for multiple labels'
				else:
					net.seeds[v] = u
			else:
				net.seeds[v] = u;

	print 'network loaded.'
	return net



