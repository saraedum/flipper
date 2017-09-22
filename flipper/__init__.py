
''' Flipper is a program for computing the action of mapping classes on
laminations on punctured surfaces using ideal triangulation coordinates.

It can decide the Nielsen--Thurston type of a given mapping class and,
for pseudo-Anosov mapping classes, construct a layered, veering
triangulation of their mapping torus, as described by Agol.

Get started by starting the GUI:
	> import flipper.app
	> flipper.app.start()
or by creating a Triangulation using the helper function:
	> flipper.create_triangulation(...)
or from an isomorphism signature:
	> flipper.create_triangulation_from_iso_sig(...)
or by loading one of the provided EquippedTriangulations using:
	> flipper.load(...) '''

import warnings

with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	import pkg_resources  # Suppress 'UserWarning: Module flipper was already imported from ...'
	__version__ = pkg_resources.require('flipper')[0].version

# We'll only import the bare minimum. This way people missing packages
# can still use the flipper kernel at least.
# import flipper.application  # Uses tkinter.
import flipper.kernel
# import flipper.example  # Uses snappy.
import flipper.doc
# import flipper.test  # Uses snappy.
import flipper.profile

from flipper.load import load
from flipper.census import census

# Set up really short names for the most commonly used classes and functions by users.
create_triangulation = flipper.kernel.create_triangulation
triangulation_from_iso_sig = flipper.kernel.triangulation_from_iso_sig
norm = flipper.kernel.norm

from numbers import Integral as IntegerType

AbortError = flipper.kernel.AbortError
ApproximationError = flipper.kernel.ApproximationError
AssumptionError = flipper.kernel.AssumptionError
ComputationError = flipper.kernel.ComputationError
FatalError = flipper.kernel.FatalError

# Finally load in the constants. These might require flipper to do the calculations
# so we can't create them before this point.
import flipper.kernel.constants
