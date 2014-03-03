
from fractions import Fraction
from math import log10 as log

import Flipper

# In Python3 we can just do round(fraction, precision) however this
# doesn't exist in Python2 so we recreate it here. 
def round_fraction(fraction, precision):
	shift = 10**precision
	shifted = fraction * shift
	floor, remainder = divmod(shifted.numerator, shifted.denominator)
	
	if remainder * 2 < shifted.denominator or (remainder * 2 == shifted.denominator and floor % 2 == 0):
		numerator = floor
	else:
		numerator = floor + 1
	
	return (numerator, precision)

class Polynomial(object):
	def __init__(self, coefficients):
		self.coefficients = coefficients
		self.height = max(abs(x) for x in self.coefficients) if self.coefficients else 1
		self.log_height = log(self.height)
		self.degree = len(self.coefficients) - 1
		self._old_root = None
		self._root = Fraction(self.height * self.degree, 1)
	
	def __iter__(self):
		return iter(self.coefficients)
	
	def __repr__(self):
		return ' + '.join('%d x^%d' % (coefficient, index) for index, coefficient in enumerate(self))
	
	def __call__(self, other):
		return sum(coefficient * other**index for index, coefficient in enumerate(self))
	
	def derivative(self):
		return Polynomial([index * coefficient for index, coefficient in enumerate(self)][1:]) 
	
	def find_leading_root(self, precision):
		f = self
		f_prime = self.derivative()
		# Iterate using Newton's method until the error becomes small enough. 
		while self._old_root is None or log(abs(self._root.denominator)) + log(abs(self._old_root.denominator)) - log(abs(self._root.numerator * self._old_root.denominator - self._old_root.numerator * self._root.denominator)) < precision:
		# while self._old_root is None or - log(abs(self._root - self._old_root)) < precision:
			self._old_root, self._root = self._root, self._root - f(self._root) / f_prime(self._root)
		
		return self._root
	
	def algebraic_approximate_leading_root(self, precision=None, power=1):
		# Returns an algebraic approximation of this polynomials leading root
		# which is correct to at least precision decimal places.
		numerator, precision = round_fraction(self.find_leading_root(precision), 2*precision)
		
		return Flipper.kernel.algebraicapproximation.algebraic_approximation_from_fraction(numerator, precision, self.degree, self.log_height)
