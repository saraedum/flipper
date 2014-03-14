
from math import log10 as log

import Flipper

# This provides us with a way of storing and manipulating elements of QQ(\lambda),
# where \lambda is an algebraic integer (however technically this can currently only actually
# manipulate elements of ZZ[\lambda]). This can even do multiplication of these 
# elements without having to drop to an AlgebraicApproximation and so is significantly
# faster that the previous way of doing this sort of calculation. 

# This requires the numbers to be given as a linear combinations of 
# 1, \lambda, ..., \lambda^{d-1}. Currently only Sage can do this.

class NumberField(object):
	def __init__(self, polynomial=None):
		if polynomial is None: polynomial = Flipper.kernel.Polynomial([-1, 1])
		
		self.polynomial = polynomial
		self.polynomial_coefficients = self.polynomial.coefficients
		self.degree = self.polynomial.degree
		
		# The expression of self.generator^d. Here we use the fact that the generator is an algebraic integer.
		self.generator_d = [-a for a in self.polynomial_coefficients[:-1]]
		
		self.log_height = self.polynomial.log_height
		self.sum_log_height_powers = self.degree * self.degree * self.log_height
		self.companion_matrices = self.polynomial.companion_matrix().powers(self.degree)
		
		self.current_accuracy = -1
		self.algebraic_approximations = [None] * self.degree  # A list of approximations of \lambda^0, ..., \lambda^(d-1).
		self.increase_accuracy(100)
		
		self.one = self.element([1])
		self.lmbda = self.element([1]) if self.is_QQ() else self.element([0, 1])
	
	def increase_accuracy(self, accuracy):
		if self.current_accuracy < accuracy:
			# Increasing the accuracy is expensive, so when we have to do it we'll get a fair amount more just to amortise the cost
			self.current_accuracy = 2 * accuracy  # We'll actually work to double what is requested.
			self.algebraic_approximations = [self.polynomial.algebraic_approximate_leading_root(self.current_accuracy, power=index) for index in range(self.degree)]
	
	def __repr__(self):
		return 'QQ[%s]' % str(self.polynomial)
	def __eq__(self, other):
		return self.polynomial == other.polynomial
	
	def element(self, linear_combination):
		return NumberFieldElement(self, linear_combination)
	
	def is_QQ(self):
		return self.degree == 1

class NumberFieldElement(object):
	def __init__(self, number_field, linear_combination):
		self.number_field = number_field
		if len(linear_combination) < self.number_field.degree:
			linear_combination = linear_combination + [0] * (self.number_field.degree - len(linear_combination))
		elif len(linear_combination) > self.number_field.degree:
			raise TypeError('Linear combination: %s has more terms than the degree of the field in which it lives' % linear_combination)
		self.linear_combination = linear_combination
		self._algebraic_approximation = None
		self.current_accuracy = -1
	
	def __repr__(self):
		return ' + '.join('%d L^%d' % (coefficient, index) for index, coefficient in enumerate(self)) + ' ~= ' + str(self.algebraic_approximation())
	def __iter__(self):
		return iter(self.linear_combination)
	def __float__(self):
		return float(self.algebraic_approximation())
	
	def __neg__(self):
		return NumberFieldElement(self.number_field, [-a for a in self])
	def __add__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number fields.')
			return NumberFieldElement(self.number_field, [a+b for a, b in zip(self, other)])
		elif isinstance(other, Flipper.kernel.Integer_Type):
			return NumberFieldElement(self.number_field, [self.linear_combination[0] + other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot subtract elements of different number fields.')
			return NumberFieldElement(self.number_field, [a-b for a, b in zip(self, other)])
		elif isinstance(other, Flipper.kernel.Integer_Type):
			return NumberFieldElement(self.number_field, [self.linear_combination[0] - other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number fields.')
			
			M = sum([a * matrix for a, matrix in zip(self, self.number_field.companion_matrices)], Flipper.kernel.Zero_Matrix(self.number_field.degree))
			return self.number_field.element(M * other.linear_combination)
		elif isinstance(other, Flipper.kernel.Integer_Type):
			return self.number_field.element([a * other for a in self])
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number fields.')
			
			return self.algebraic_approximation(multiplicative_error=3) / other.algebraic_approximation(multiplicative_error=3) 
		elif isinstance(other, Flipper.kernel.types.Integer_Type):
			return self.algebraic_approximation(multiplicative_error=3) / other
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	
	def __lt__(self, other):
		return (self - other).is_negative()
	def __eq__(self, other):
		return (self - other).is_zero()
	def __gt__(self, other):
		return (self - other).is_positive()
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other
	
	def is_positive(self):
		return self.algebraic_approximation().is_positive()
	def is_negative(self):
		return self.algebraic_approximation().is_negative()
	def is_zero(self):
		return not self.is_positive() and not self.is_negative()
	
	def algebraic_approximation(self, accuracy=None, multiplicative_error=1, additive_error=0):
		# If no accuracy is given, calculate how much accuracy is needed to ensure that
		# the AlgebraicApproximation produced is well defined.
		
		# Let N = QQ(\lambda) and d := N.degree.
		N = self.number_field
		d = N.degree
		# Let [a_i] := self.linear_combination, [\alpha_i] := \lambda^i.algebraic_approximations and [I_i] := [\alpha_i.interval].
		# Let \alpha := sum(a_i * \alpha_i) and I := \alpha.interval = sum(a_i * I_i)
		# As \alpha also lies in K = QQ(\lambda) it also has degree at most d.
		#
		# Now if acc(I_i) >= k then acc(I) >= k - (d-1) [Interval.py L:13].
		# Additionally, 
		#	log(height(\alpha)) <= sum(log(height(a_i \alpha_i))) + d log(2) <= sum(log(a_i)) + sum(log(height(\alpha_i))) + d log(2) [AlgebraicApproximation.py L:9].
		# Hence for \alpha to determine a unique algebraic number we need that:
		#	acc(I) >= log(d) + log(height(\alpha)).
		# That is:
		#	k - (d-1) >= log(d) + sum(log(a_i)) + sum(log(height(\alpha_i))) + d log(2).
		# or equivalently that:
		#	k >= sum(log(a_i)) + N.sum_log_height_powers + log(d) + (d-1) + d log(2).
		#
		# Therefore we start by setting the accuracy of each I_i to at least:
		#	int(sum(log(a_i)) + N.sum_log_height_powers + log(N.degree) + 2*d).
		if accuracy is None: accuracy = int(sum(Flipper.kernel.algebraicapproximation.log_height_int(coefficient) for coefficient in self) + N.sum_log_height_powers + log(d) + 2*d)
		accuracy = accuracy * multiplicative_error + additive_error
		
		if self._algebraic_approximation is None or self.current_accuracy < accuracy:
			N.increase_accuracy(accuracy)  # Increase the accuracy so the calculation will work.
			# Actually this will probably be too precise.
			
			# Watch out there is an all zeros case to worry about. We'll be careful but this should never be used though.
			if all(a == 0 for a in self):
				self._algebraic_approximation = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_int(0, 2*accuracy, self.number_field.degree, 1)
			else:
				self._algebraic_approximation = sum(a * generator_approximation for a, generator_approximation in zip(self, N.algebraic_approximations))
			
			self.current_accuracy = self._algebraic_approximation.interval.accuracy
			# Now if accuracy was not None then self.current_accuracy >= accuracy.
		
		return self._algebraic_approximation
	
	def algebraic_hash_ratio(self, other):
		# !?! RECHEK THIS AGAINST Interval.py.
		HASH_DENOMINATOR = 30
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()

def number_field_from_integers(integers):
	N = NumberField()
	return [N.element([integer]) for integer in integers]
