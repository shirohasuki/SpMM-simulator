from scipy.sparse import csr_matrix, csc_matrix, coo_matrix

class SparseRepresentFormat:
    def __init__(self, dense_matrix, format):
        if (format == 'csr'):
            self.sparse_matrix = self.density_to_csr(dense_matrix)
        elif (format == 'csc'):
            self.sparse_matrix = self.density_to_csc(dense_matrix)
        elif (format == 'coo'):
            self.sparse_matrix = self.density_to_coo(dense_matrix)    
        elif (format == 'xyv_coo'): # 内部总线协议
            self.sparse_matrix = self.xyv_to_coo(dense_matrix)
        else: 
            self.sparse_matrix = 0
    def density_to_csr(self, dense_matrix):
        return csr_matrix(dense_matrix)
    def density_to_csc(self, dense_matrix):
        return csc_matrix(dense_matrix)
    
    def density_to_coo(self, dense_matrix):
        return coo_matrix(dense_matrix)
    
    def xyv_to_coo(self, xyv_matrix):
        return coo_matrix((xyv_matrix[2], (xyv_matrix[0], xyv_matrix[1])))


if __name__ == '__main__':
    dense_matrix = [
        [1, 0, 0],
        [0, 2, 0],
        [3, 0, 4]
    ]
    
    csr_format = SparseRepresentFormat(dense_matrix, 'csr')
    csc_format = SparseRepresentFormat(dense_matrix, 'csc')
    coo_format = SparseRepresentFormat(dense_matrix, 'coo')
    
    # Print the sparse matrix in CSR format
    print(csr_format.sparse_matrix)
    print(csc_format.sparse_matrix)
    print(coo_format.sparse_matrix)
    
    # Optionally, print the individual components (data, indices, indptr)
    print("Data:", csr_format.sparse_matrix.data)
    print("Indices:", csr_format.sparse_matrix.indices)
    print("Indptr:", csr_format.sparse_matrix.indptr)
    
