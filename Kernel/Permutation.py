
from itertools import combinations

# Represents a permutation on N elements.
class Permutation:
	def __init__(self, permutation):
		assert(set(permutation) == set(range(len(permutation))))
		self.permutation = tuple(permutation)
	def __repr__(self):
		return str(self.permutation)
	def __iter__(self):
		return iter(self.permutation)
	def __getitem__(self, index):
		return self.permutation[index]
	def __len__(self):
		return len(self.permutation)
	def __mul__(self, other):
		assert(len(self) == len(other))
		return Permutation([self[other[i]] for i in range(len(self))])
	def __str__(self):
		return ''.join(str(p) for p in self.permutation)
	def __eq__(self, other):
		return self.permutation == other.permutation
	def inverse(self):
		return Permutation([j for i in range(len(self)) for j in range(len(self)) if self[j] == i])
	def is_even(self):
		even = True
		for j, i in combinations(range(len(self)),2):
			if self[j] > self[i]: even = not even
		return even
	def embed(self, n):
		# Returns the permutation given by including this permutation into Sym(n). Assumes n >= len(self).
		assert(n >= len(self))
		return Permutation(list(self.permutation) + list(range(len(self),n)))

#### Some special Permutations we know how to build.

def Id_Permutation(n):
	return Permutation(range(n))

def cyclic_permutation(cycle, n):
	return Permutation([(cycle + i) % n for i in range(n)])

def permutation_from_mapping(n, mapping, even):
	for perm in permutations(range(n), n):
		P = Permutation(perm)
		if P.is_even() == even and all(P[source] == target for (source, target) in mapping):
			return P
	
	raise TypeError('Not a valid permutation.')  # !?! To Do.
