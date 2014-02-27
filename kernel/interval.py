
from math import log10 as log

import Flipper

# This class represents the interval (lower / 10^precision, upper / 10^precision).

# For an interval I let acc(I) denote the accuracy of I, that is
#	acc(I) := self.precision - int(log(self.upper - self.lower)).
# For an integer x let log+(x) := log(max(abs(x), 1)) and for an interval I
# let log+(I) := max(log+(I.lower), log+(I.upper), I.precision) - I.precision.

# Suppose that x is an integer and that I and J are intervals and that 
# m := min(acc(I), acc(J)).
# Then we obtain the following bounds:
#	acc(I + J) >= m - 1,
#	acc(I * J) >= m - log(I.lower + J.lower + 1)
#	acc(I / J) >= m - log+(J)
#	acc(x * I) >= acc(I) - log+(x)

class Interval(object):
	# __slots__ = ['lower', 'upper', 'precision', 'accuracy', 'log_plus']  # Force minimal RAM usage.
	
	def __init__(self, lower, upper, precision):
		if lower == upper: 
			lower, upper = lower-1, upper+1
			raise Flipper.ApproximationError
		assert(lower < upper)
		
		self.lower = lower
		self.upper = upper
		self.precision = precision
		# The width of this interval is at most 10^-self.accuracy.
		# That is, this interval defines a number correct to self.accuracy decimal places.
		self.accuracy = self.precision - int(log(self.upper - self.lower))
		self.log_plus = int(max(log(max(abs(self.lower), 1)) - self.precision, log(max(abs(self.upper), 1)) - self.precision, 1)) + 1 
	
	def __repr__(self):
		return self.approximate_string(6)
	
	def __float__(self):
		return float(self.upper + self.lower) / (2 * 10**self.precision)
	
	def approximate_string(self, accuracy=None):
		if accuracy is None or accuracy > self.accuracy: accuracy = self.accuracy-1
		s = str(self.lower).zfill(self.precision + (1 if self.lower >= 0 else 2))
		return '%s.%s?' % (s[:len(s)-self.precision], s[len(s)-self.precision:len(s)-self.precision+accuracy])
	def interval_string(self):
		# Remember to take into account that the '-' sign uses a character.
		s = str(self.lower).zfill(self.precision + (1 if self.lower >= 0 else 2))
		t = str(self.upper).zfill(self.precision + (1 if self.upper >= 0 else 2))
		return '(%s.%s, %s.%s)' % (s[:len(s)-self.precision], s[len(s)-self.precision:], t[:len(t)-self.precision], t[len(t)-self.precision:])
	def tuple(self):
		return (self.lower, self.upper, self.precision)
	def change_denominator(self, new_denominator):
		d = new_denominator - self.precision
		if d > 0:
			return Interval(self.lower * 10**d, self.upper * 10**d, new_denominator)
		elif d == 0:
			return self
		elif d < 0:
			return Interval(self.lower // 10**(-d), 1 + self.upper // 10**(-d), new_denominator)
	def __contains__(self, other):
		if isinstance(other, Interval):
			return self.lower < other.lower and other.upper < self.upper
		elif isinstance(other, Flipper.Integer_Type):
			return self.lower < other * 10**self.precision < self.upper
		else:
			return NotImplemented
	def __neg__(self):
		return Interval(-self.upper, -self.lower, self.precision)
	def __add__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			new_lower = P.lower + Q.lower
			new_upper = P.upper + Q.upper
			return Interval(new_lower, new_upper, common_precision)
		elif isinstance(other, Flipper.Integer_Type):
			return Interval(self.lower + other * 10**self.precision, self.upper + other * 10**self.precision, self.precision)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			new_lower = P.lower - Q.upper
			new_upper = P.upper - Q.lower
			return Interval(new_lower, new_upper, common_precision)
		elif isinstance(other, Flipper.Integer_Type):
			return Interval(self.lower - other * 10**self.precision, self.upper - other * 10**self.precision, self.precision)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			values = [P.lower * Q.lower, P.upper * Q.lower, P.lower * Q.upper, P.upper * Q.upper]
			return Interval(min(values), max(values), 2*common_precision)
		elif isinstance(other, Flipper.Integer_Type):
			# Multiplication by 0 could cause problems here as these represent open intervals.
			if other == 0: return 0
			
			values = [self.lower * other, self.upper * other]
			return Interval(min(values), max(values), self.precision)
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Interval):
			if 0 in other:
				raise Flipper.ApproximationError('Denominator contains 0.')
			# !?! RECHECK THIS!
			common_precision = max(self.precision, other.precision) + other.log_plus
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			values = [P.lower * 10**common_precision // Q.lower, P.upper * 10**common_precision // Q.lower, P.lower * 10**common_precision // Q.upper, P.upper * 10**common_precision // Q.upper]
			return Interval(min(values), max(values), common_precision)
		elif isinstance(other, Flipper.Integer_Type):
			values = [self.lower // other, self.upper // other]
			return Interval(min(values), max(values), self.precision)
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		if isinstance(other, Flipper.Integer_Type):
			# !?! RECHECK THIS!
			return interval_from_int(other, self.precision) / self
		else:
			return NotImplemented
	def __rtruediv__(self, other):
		return self.__rdiv__(other)

#### Some special Intervals we know how to build.

def interval_from_string(string):
	i, r = string.split('.') if '.' in string else (string, '')
	x = int(i + r)
	return Interval(x-1, x+1, len(r))

def interval_from_int(integer, accuracy):
	x = integer * 10**accuracy
	return Interval(x-1, x+1, accuracy)

def interval_from_fraction(numerator, denominator, accuracy):
	x = numerator * 10**accuracy // denominator
	return Interval(x-1, x+1, accuracy)
