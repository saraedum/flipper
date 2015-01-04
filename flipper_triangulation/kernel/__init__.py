
''' The flipper kernel. '''

from . import algebraicapproximation
from . import algebraicnumber
from . import encoding
from . import error
from . import equippedtriangulation
from . import interval
from . import isometry
from . import lamination
from . import matrix
from . import numberfield
from . import permutation
from . import polynomial
from . import splittingsequence
from . import symboliccomputation
from . import triangulation
from . import triangulation3
from . import types
from . import utilities

# Set up shorter names for all of the different classes.
Vertex = triangulation.Vertex
Edge = triangulation.Edge
Triangle = triangulation.Triangle
Triangulation = triangulation.Triangulation
Corner = triangulation.Corner
AlgebraicApproximation = algebraicapproximation.AlgebraicApproximation
LFunction = encoding.LFunction
PartialFunction = encoding.PartialFunction
BasicPLFunction = encoding.BasicPLFunction
PLFunction = encoding.PLFunction
Encoding = encoding.Encoding
AbortError = error.AbortError
ApproximationError = error.ApproximationError
AssumptionError = error.AssumptionError
ComputationError = error.ComputationError
EquippedTriangulation = equippedtriangulation.EquippedTriangulation
Interval = interval.Interval
Isometry = isometry.Isometry
Lamination = lamination.Lamination
Matrix = matrix.Matrix
NumberField = numberfield.NumberField
PolynomialRoot = polynomial.PolynomialRoot
AlgebraicMonomial = algebraicnumber.AlgebraicMonomial
AlgebraicNumber = algebraicnumber.AlgebraicNumber
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence
Triangulation3 = triangulation3.Triangulation3

id_matrix = matrix.id_matrix
zero_matrix = matrix.zero_matrix
dot = matrix.dot
height_int = algebraicnumber.height_int
norm = triangulation.norm
id_l_function = encoding.id_l_function
id_pl_function = encoding.id_pl_function
zero_pl_function = encoding.zero_pl_function
IntegerType = types.IntegerType
StringType = types.StringType
NumberType = types.NumberType

# Functions that help with construction.
create_triangulation = triangulation.create_triangulation
create_algebraic_approximation = algebraicapproximation.create_algebraic_approximation
create_polynomial_root = polynomial.create_polynomial_root
create_algebraic_number = algebraicnumber.create_algebraic_number
create_interval = interval.create_interval
create_number_field = numberfield.create_number_field

package = utilities.package
product = utilities.product
gcd = utilities.gcd

