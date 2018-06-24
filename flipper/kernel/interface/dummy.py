
''' A module for a dummy interface. '''

import flipper

def gram_schmidt(basis):
    ''' Return an orthonormal basis for the subspace generated by basis. '''
    
    basis = [list(row) for row in basis]
    
    dot = flipper.kernel.dot
    for i in range(len(basis)):
        for j in range(i):
            a, b = dot(basis[i], basis[j]), dot(basis[j], basis[j])
            basis[i] = [b * x - a * y for x, y in zip(basis[i], basis[j])]
    return basis

def project(vector, basis):
    ''' Return the projection of vector to the subspace generated by basis. '''
    
    dot = flipper.kernel.dot
    orthogonal_basis = gram_schmidt(basis)
    linear_combination = [dot(vector, row) / dot(row, row) for row in orthogonal_basis]
    return [sum(a * b[i] for a, b in zip(linear_combination, orthogonal_basis)) for i in range(len(vector))]

def directed_eigenvector(action_matrix, condition_matrix):
    ''' An implementation of flipper.kernel.symboliccomputation.directed_eigenvector() using pure Python.
    
    See the docstring of the above function for further details. '''
    
    dot = flipper.kernel.dot
    # Getting the square free representative makes this faster.
    eigenvalues = [eigenvalue.irreducible_representation() for eigenvalue in action_matrix.characteristic_polynomial().square_free().real_roots() if eigenvalue > 1]
    
    for eigenvalue in sorted(eigenvalues, reverse=True):
        # We will calculate the eigenvector ourselves.
        N = flipper.kernel.NumberField(eigenvalue)
        kernel_basis = (action_matrix - N.lmbda).kernel()  # Sage is much better at this than us for large matrices.
        if len(kernel_basis) == 1:  # If rank(kernel) == 1.
            [eigenvector] = kernel_basis
            
            # We might need to flip the eigenvector if we have the inverse basis.
            if sum(eigenvector) < 0: eigenvector = [-x for x in eigenvector]
            
            if flipper.kernel.matrix.nonnegative(eigenvector) and condition_matrix.nonnegative_image(eigenvector):
                return N.lmbda, eigenvector
        else:
            M = (flipper.kernel.id_matrix(condition_matrix.width).join(condition_matrix)) * kernel_basis.transpose()
            try:
                linear_combination = M.find_vector_with_nonnegative_image()
                return N.lmbda, kernel_basis.transpose()(linear_combination)
            except flipper.AssumptionError:  # Eigenspace is disjoint from the cone.
                pass
    
    raise flipper.ComputationError('No interesting eigenvalues in cell.')

