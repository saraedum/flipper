
# This module is designed for manipulating approximations of real algebraic numbers via intervals.

# Suppose that f(x) = a_n x^n + ... + a_0 \in ZZ[x] is a (not necessarily irreducible) polynomial with a_n != 0. We define
# h(f) := log(max(|a_n|)) to be its height and deg(f) := n to be its degree.
#
# Let K be a number field and x_0 \in K be an algebraic number. We define h(x_0) := h(minpoly(x_0)) to be its the height 
# and deg(x_0) := deg(minpoly(x_0)) to be its degree.

# We use the following facts:
#	1a) For x_0, x_1 \in K, h(x_0 +/- x_1) <= h(x_0) + h(x_1) + 1,
#	 b) h(x_0 * x_1) <= h(x_0) + h(x_1) and
#	 c) h(1 / x_0) == h(x_0) [Waldschmidt "Diophantine approximation on linear algebraic groups", Property 3.3].
#	2) If 0 != x_0 \in K is a root of f(x) = a_n x^n + ... + a_0 then 
#		|x_0| >= 1 / sum(|a_i / a_0|) [Basu et al. "Algorithms in Real Algebraic Geometry", Lemma 10.3].

# An immediate consequence of 1) is that if x_0 \in K is a root of f \in ZZ[x] then h(x_0) <= h(f) + 2 \deg(f).

# From 2) it follows that so long as the accuracy of the interval of an AlgebraicApproximation is at least
#	-log(1 / sum(|a_i / a_0|)) = log(sum(|a_i / a_0|)) <= log(sum(|a_i|)) <= log(deg(x_0) * H(f)) <= log(deg(x_0)) + h(x_0)
# then it uniquely determines an algebraic number.

# Thus by knowing a sufficiently accurate approximation of x_0 we can determine if x_0 > 0. Combining this with 1) we can 
# therefore determine if x_0 > x_1 by determining if (x_0 - x_1) > 0.

import flipper

from math import log10 as log
log_2 = log(2)

class AlgebraicApproximation(object):
	''' This represents an algebraic number. It uses an interval, which is sufficiently small based 
	on the degree and height of the number to uniquely determine it. '''
	def __init__(self, interval, log_degree, height):
		''' This class uses a sufficiently small interval to represent an algebraic number exactly. It is specified
		by an interval with contains the number, an upper bound on the log of the degree of the field extension in 
		which this number lives and an upper bound on the height of this number. '''
		assert(isinstance(interval, flipper.kernel.Interval))
		assert(isinstance(log_degree, flipper.kernel.Number_Type))
		assert(isinstance(height, flipper.kernel.Number_Type))
		
		self.interval = interval
		self.log_degree = log_degree
		self.accuracy = self.interval.accuracy
		# We need to make sure that 10^self.height >= height(algebraic number) in order to maintain an upper bound.
		# This is a bit of a hack and eventually I might find a better way to do this but at least for now it works.
		self.height = round(height, 5) + 0.00001
		self.accuracy_needed = int(self.log_degree) + int(self.height) + 2
		# An algebraic approximation is good if it is known to more places
		# than its accuracy needed. That is if self.interval.accuracy >= self.accuracy_needed.
		if self.accuracy < self.accuracy_needed:
			raise flipper.kernel.ApproximationError('An algebraic number with log(degree) at most %d and height at most %0.3f requires an interval with accuracy at least %d not %d.' % (self.log_degree, self.height, self.accuracy_needed, self.accuracy))
	
	def __repr__(self):
		return repr((self.interval, self.log_degree, self.height))
	
	def __float__(self):
		return float(self.interval)
	
	def change_denominator(self, new_denominator):
		return AlgebraicApproximation(self.interval.change_denominator(new_denominator), self.log_degree, self.height)
	def change_accuracy(self, new_accuracy):
		return AlgebraicApproximation(self.interval.change_accuracy(new_accuracy), self.log_degree, self.height)
	def simplify(self):
		return AlgebraicApproximation(self.interval.simplify(), self.log_degree, self.height)
	
	def __neg__(self):
		return AlgebraicApproximation(-self.interval, self.log_degree, self.height)
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval + other.interval, self.log_degree + other.log_degree, self.height + other.height + log_2)
		elif isinstance(other, flipper.Integer_Type):
			return AlgebraicApproximation(self.interval + other, self.log_degree, self.height + flipper.kernel.height_int(other) + log_2)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval - other.interval, self.log_degree + other.log_degree, self.height + other.height + log_2)
		elif isinstance(other, flipper.Integer_Type):
			return AlgebraicApproximation(self.interval - other, self.log_degree, self.height + flipper.kernel.height_int(other) + log_2)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval * other.interval, self.log_degree + other.log_degree, self.height + other.height)
		elif isinstance(other, flipper.Integer_Type):
			return AlgebraicApproximation(self.interval * other, self.log_degree, self.height + flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		if power == 0:
			return algebraic_approximation_from_integer(1)
		if power > 0:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
	def __div__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval / other.interval, self.log_degree + other.log_degree, self.height + other.height)
		elif isinstance(other, flipper.Integer_Type):
			return AlgebraicApproximation(self.interval / other, self.log_degree, self.height + flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		if isinstance(other, flipper.Integer_Type):
			return AlgebraicApproximation(other / self.interval, self.log_degree, self.height + flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	def is_positive(self):
		return self.interval.lower > 0
	def is_negative(self):
		return self.interval.upper < 0
	def is_zero(self):
		return not self.is_positive() and not self.is_negative()
	
	def __lt__(self, other):
		return (self - other).is_negative()
	def __eq__(self, other):
		return (self - other).is_zero()
	def __gt__(self, other):
		return (self - other).is_positive()
	def __ne__(self, other):
		return not self == other
	
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other

#### Some special Algebraic approximations we know how to build.
# These are useful for creating tests.

def algebraic_approximation_helper(string, degree, height):
	return AlgebraicApproximation(flipper.kernel.interval_helper(string), log(max(degree, 1)), height)

def algebraic_approximation_from_integer(integer):
	return AlgebraicApproximation(flipper.kernel.interval.interval_from_integer(integer), 0, 1)

