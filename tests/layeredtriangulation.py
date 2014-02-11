
from __future__ import print_function

import Flipper

def build_bundle(word, isometry_number):
	Example = Flipper.examples.abstracttriangulation.Example_S_1_1
	word, mapping_class = Flipper.examples.abstracttriangulation.build_example_mapping_class(Example, word)
	# !?! Could throw an ImportError if no SymbolicComputation library is present.
	preperiodic, periodic, new_dilatation, lamination, isometries = mapping_class.invariant_lamination().splitting_sequence()
	
	L = Flipper.kernel.layeredtriangulation.Layered_Triangulation(lamination.abstract_triangulation, word)
	L.flips(periodic)
	closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in isometries)]
	try:
		M = L.close(closing_isometries[isometry_number])
	except IndexError:
		return None
	
	return M.SnapPy_string()

def main():
	try:
		S = __import__('snappy')
	except ImportError:
		print('SnapPy unavailable, tests skipped.')
		return True
	
	tests = [
		('aB', 0, 'm003'),
		('aB', 1, 'm004'),
		('Ba', 0, 'm003'),
		('Ba', 1, 'm004'),
		('Ab', 0, 'm003'),
		('Ab', 1, 'm004'),
		('bA', 0, 'm003'),
		('bA', 1, 'm004')
		]
	
	for word, isometry_number, target_manifold in tests:
		M = build_bundle(word, isometry_number)
		if M is None or not S.Manifold(M).is_isometric_to(S.Manifold(target_manifold)):
			print(word, isometry_number, target_manifold)
			return False
	
	# try:
		# T = __import__('twister')
	# except ImportError:
		# print('Twister unavailable, tests skipped.')
		# return True
	
	# for _ in range(50):
		# word, mapping_class = build_example_mapping_class(Example, random_length=10)
		
		# print(word)
		# try:
			# M = T.Surface('S_1_1').bundle(word)
			# N0 = S.Manifold(build_bundle(word, 0))
			# N1 = S.Manifold(build_bundle(word, 1))
			# if not M.is_isometric_to(N0) and not M.is_isometric_to(N1):
				# print(M.volume())
				# print(word)
				# return False
		# except (Flipper.kernel.error.AssumptionError, Flipper.kernel.error.ComputationError):
			# print('Not pA.')
	
	return True

if __name__ == '__main__':
	print(main())
