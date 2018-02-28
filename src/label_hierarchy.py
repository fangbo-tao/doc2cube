
class LNode:

	def __init__(self, path):
		self.path = path
		segs = path.split('|')
		self.name = segs[-1]
		if path != '*':
			self.level = len(segs)
		else:
			self.level = 0
		self.children = []
		self.parent = None

	def __str__(self):
		return self.path

	def __unicode__(self):
		return self.path

	def set_parent(self, parent):
		self.parent = parent

	def add_child(self, child):
		for t_child in self.children:
			if t_child.path == child.path:
				return
		self.children.append(child)

	def get_ascendant(self, level=1):
		if self.level < level or level < 0:
			print 'Specified level not correct!'
			exit(1)
		asc = self
		for i in range(self.level - level):
			asc = asc.parent
		return asc


class Hierarchy:

	def __init__(self, f_file):
		self.root = LNode('*')
		self.all_nodes = {'*':self.root}

		with open(f_file, 'r') as f:
			for line in f:
				segs = line.strip('\r\n').split('\t')
				if segs[1] == '*':
					continue
				if segs[1] not in self.all_nodes:
					parts = segs[1].split('|')
					self.add_node(parts, segs[1])


	def add_node(self, parts, path):
		# print 'adding ' + path
		node = LNode(path)
		self.all_nodes[path] = node
		last_node = node
		for i in range(len(parts) - 1, 0, -1):
			p_path = '|'.join(parts[:i])
			if p_path in self.all_nodes:
				parent = self.all_nodes[p_path]
			else:
				parent = LNode(p_path)
				self.all_nodes[p_path] = parent
			parent.add_child(last_node)
			last_node.set_parent(parent)
			last_node = parent
		self.root.add_child(last_node)
		last_node.set_parent(self.root)
		# print self.all_nodes


	def get_nodes_at_level(self, level):
		result_nodes = []
		for node in self.all_nodes.values():
			if node.level == level:
				result_nodes.append(node)
		return result_nodes

	def get_all_nodes(self):
		result_nodes = []
		for node in self.all_nodes.values():
			if node.level != 0:
				result_nodes.append(node)
		return result_nodes

	def get_node(self, path):
		return self.all_nodes[path]


