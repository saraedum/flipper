
from __future__ import print_function

import flipper

def main(verbose=False):
	
	# !?! TO DO.
	
	try:
		N = flipper.kernel.number_field_helper([-2, 0, 1], '1.41')  # QQ(sqrt(2)).
		x = N.lmbda  # sqrt(2)
		assert(x * x == 2)
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

