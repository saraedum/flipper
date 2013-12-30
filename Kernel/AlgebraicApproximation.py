
# A library for manipulating real algebraic numbers via interval approximations.

# Let K := QQ(\lambda) be a number field.
# Suppose that x, y \in K.
# If x has minimal polynomial a_n x^n + ... + a_0 then 
# let deg(x) := n be the degree of x and height(x) := max(|a_n|).

# We use the following facts:
#	1a) height(x +/- y) <= 2 * height(x) * height(y)
#	 b) height(x *// y) <= height(x) * height(y) [Waldschmidt "Diophantine approximation on linear algebraic groups", Property 3.3].
#	2) If x != 0 then |x| >= 1 / sum(|a_i / a_0|) [Basu et al. "Algorithms in Real Algebraic Geometry", Lemma 10.3]. 

# From 1) we can obtain an upper bound on the height of an equation of algebraic numbers. See:
#	http://mathoverflow.net/questions/64643/height-of-algebraic-numbers

# From 2) it follows that so long as the accuracy of the interval of an Algebraic_Approximation is at least
#	-log(1 / sum(|a_i / a_0|)) = log(sum(|a_i / a_0|)) <= log(sum(|a_i|)) <= log(deg(x) * height(x)) = log(deg(x)) + log(height(x))
# it uniquely determines an algebraic number.

# Thus by knowing a sufficiently accurate approximation of x we can determine if x > 0. Combining this with 1) we can 
# therefore determine if x > y by determining if (x - y) > 0.

from math import log10 as log

from Flipper.Kernel.Interval import Interval, interval_from_string, interval_epsilon
from Flipper.Kernel.Error import AssumptionError, ApproximationError
from Flipper.Kernel.SymbolicComputation import symbolic_approximate, symbolic_degree, symbolic_height, algebraic_type

def log_height(number):
	return log(symbolic_height(number))

# This class uses a sufficiently small interval to represent an algebraic number exactly.
class Algebraic_Approximation:
	def __init__(self, interval, degree, log_height):
		self.interval = interval
		self.degree = degree
		# We need to make sure that 10^self.log_height >= height(algebraic number) in order to maintain an upper bound.
		# This is a bit of a hack and eventually I might find a better way to do this 
		# but at least for now it works.
		self.log_height = round(log_height, 5) + 0.00001
		self.accuracy_needed = int(log(self.degree)) + int(self.log_height) + 2
		# An algebraic approximation is good if it is known to more interval places
		# than its accuracy needed. That is if self.interval.accuracy >= self.accuracy_needed.
		if self.interval.accuracy < self.accuracy_needed:
			raise ApproximationError('%s may not define a unique algebraic number with degree at most %d and height at most %d.' % (self.interval, self.degree, self.log_height))
	def change_denominator(self, new_q):
		return Algebraic_Approximation(self.interval.change_denominator(new_q), self.degree, self.log_height)
	def __repr__(self):
		return repr((self.interval, self.degree, self.log_height))
	def __neg__(self):
		return Algebraic_Approximation(-self.interval, self.degree, self.log_height)
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval + other.interval, self.degree, self.log_height + other.log_height + 2)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.interval + other, self.degree, self.log_height + log_height(other) + 2)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval - other.interval, self.degree, self.log_height + other.log_height + 2)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.interval - other, self.degree, self.log_height + log_height(other) + 2)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval * other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, int):
			# Multiplication by 0 would cause problems here as we work with open intervals.
			if other == 0: return 0
			return Algebraic_Approximation(self.interval * other, self.degree, self.log_height + log_height(other))
		else:
			return NotImplemented
	def __rmult__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval / other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.interval / other, self.degree, self.log_height + log_height(other))
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		return NotImplemented  # !?!
	# These may raise ApproximationError if not enough accuracy is present.
	def __lt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.interval - other.interval < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		elif isinstance(other, int):
			return self.interval - other < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return -interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other.interval < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		elif isinstance(other, int):
			return -interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other.interval
		elif isinstance(other, int):
			return interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other
		else:
			return NotImplemented
	def __hash__(self):
		return hash((self.interval, self.degree, self.log_height))

#### Some special Algebraic approximations we know how to build.

def algebraic_approximation_from_string(string, degree, log_height):
	return Algebraic_Approximation(interval_from_string(string), degree, log_height)

def algebraic_approximation_from_symbolic(number, accuracy):
	if isinstance(number, algebraic_type):
		A = algebraic_approximation_from_string(symbolic_approximate(number, accuracy), symbolic_degree(number), log(symbolic_height(number)))
		assert(A.interval.accuracy >= accuracy)
		return A
	elif isinstance(number, int):
		return algebraic_approximation_from_string(str(number) + '.' + '0' * accuracy, 1, log_height(number))
	else:
		raise TypeError

if __name__ == '__main__':
	x = algebraic_approximation_from_string('1.4142135623730951', 2, 2)
	y = algebraic_approximation_from_string('1.41421356237', 2, 2)
	z = algebraic_approximation_from_string('1.000', 2, 2)
	
	print(z != y)
	print(x == y)
	print(x + y == x + x)
	print(x * x == 2)
	print(y * y == 2)
	print(y * y + x == 2 + x)
	print(x * x == y * y)
	print((x + x) > 0)
	print(hash(x))
