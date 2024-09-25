import numpy as np
from format import SparseRepresentFormat

class SparseReorder:
    def __init__(self, A_matrix, B_matrix, A_sparsity=True, B_sparsity=False, mode="indirection", return_seq="access"):
        assert A_sparsity != False, "A must be sparse"
        assert not ((A_sparsity and B_sparsity == False) and (mode == "intersection")), \
                "one-side sparsity please use indirection mode"
        assert not ((A_sparsity and B_sparsity == True) and (mode == "indirection")), \
                "two-side sparsity please use Intersection mode"
        
        self.a = A_matrix
        self.b = B_matrix
        
        self.a_seq = 0
        self.b_seq = 0
        
        # indirection是基于CSR的数据格式
        if (mode == 'indirection'):
            if (return_seq == 'access'):
                self.a_seq, self.b_seq, _, __ = self.indirection(self.a, self.b)
            elif (return_seq == 'value'):
                self.a_seq, self.b_seq, _, __ = self.indirection(self.a, self.b)
            else:
                self.a_seq = 0  
                self.b_seq = 0
        # intersection是基于CSR(A)与CSC(B)的数据格式
        elif (mode == 'intersection'): 
            if (return_seq == 'access'):
                _, __, self.a_seq, self.b_seq = self.intersection(self.a, self.b)
            elif (return_seq == 'value'):
                _, __, self.a_seq, self.b_seq = self.intersection(self.a, self.b)
            else:
                self.a_seq = 0  
                self.b_seq = 0
        else: 
            self.a_seq = 0  
            self.b_seq = 0

    def indirection(self, A_matrix, B_matrix):
        A_access_seq = []
        B_access_seq = []
        A_value_seq = []
        B_value_seq = []
        # A_matrix is in CSR format
        for row_idx in range(A_matrix.shape[0]):
            row_start = A_matrix.indptr[row_idx]
            row_end = A_matrix.indptr[row_idx + 1]
            
            a_block = A_matrix.data[row_start:row_end]
            col_indices = A_matrix.indices[row_start:row_end] # b的列索引

            # Get corresponding values from B_matrix based on column indices
            b_block = B_matrix[:, col_indices]
            
            # A_access_seq.append(np.arange(row_start, row_end))
            A_access_seq.append(col_indices)
            B_access_seq.append(col_indices) # Vectorized access
            A_value_seq.append(a_block)
            B_value_seq.append(b_block)
             
        # 都是返回gate_matrix
        return A_access_seq, B_access_seq, A_value_seq, B_value_seq
    
    def intersection(self, A_matrix, B_matrix):
        A_access_seq = []
        B_access_seq = []
        A_value_seq = []
        B_value_seq = []
        
        # 遍历 A 的每一行（CSR格式）
        for row_idx in range(A_matrix.shape[0]):
            a_row_start = A_matrix.indptr[row_idx]
            a_row_end = A_matrix.indptr[row_idx + 1]
            a_col_indices = A_matrix.indices[a_row_start:a_row_end]  # A矩阵的列索引（非零元素）
            
            # 针对 A 的每一行，遍历 B 的每一列（CSC格式）
            for col_idx in range(B_matrix.shape[1]):
                b_col_start = B_matrix.indptr[col_idx]
                b_col_end = B_matrix.indptr[col_idx + 1]
                b_row_indices = B_matrix.indices[b_col_start:b_col_end]  # B矩阵的行索引（非零元素）

                # 找到 A 的行的非零列和 B 的列的非零行的交集
                common_indices = np.intersect1d(a_col_indices, b_row_indices, assume_unique=True)

                # if len(common_indices) > 0:
                # A 和 B 的交集对应的值
                a_values = A_matrix.data[a_row_start:a_row_end][np.isin(a_col_indices, common_indices)]
                b_values = B_matrix.data[b_col_start:b_col_end][np.isin(b_row_indices, common_indices)]
                A_value_seq.append(a_values)
                B_value_seq.append(b_values)
                
                a_access = np.arange(a_row_start, a_row_end)[np.isin(a_col_indices, common_indices)]
                b_access = np.arange(b_col_start, b_col_end)[np.isin(b_row_indices, common_indices)]
                A_access_seq.append(a_access)
                B_access_seq.append(b_access)
                

        return A_access_seq, B_access_seq, A_value_seq, B_value_seq



if __name__ == '__main__':
    A = ([[5, 0, 7, 0],
        [0, 9, 0, 10],
        [6, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 8, 0]
    ])
    A_sparse = SparseRepresentFormat(A, 'csr').sparse_matrix
    A_sparse_csc = SparseRepresentFormat(A, 'csc').sparse_matrix
    
    B = np.array([
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
        [17, 18, 19, 20],
        [17, 18, 19, 20]
    ]) # 密集矩阵


    # 假设单边稀疏，使用indirection模式
    reorder1 = SparseReorder(A_sparse, B, A_sparsity=True, B_sparsity=False, mode="indirection", return_seq="access")
    # A_access_seq, B_access_seq= reorder1.a_seq, reorder1.b_seq
    A_access_seq, B_access_seq, A_value_seq, B_value_seq= reorder1.indirection(A_sparse, B)
    print("Indirection Mode:")
    print("A_access_seq:", A_access_seq)
    print("B_access_seq:", B_access_seq)
    # print("A_value_seq:", A_value_seq)
    # print("B_value_seq:", B_value_seq)
    
    # 假设双边稀疏，使用intersection模式
    reorder2 = SparseReorder(A_sparse, A_sparse_csc, A_sparsity=True, B_sparsity=True, mode="intersection", return_seq="access")
    # A_access_seq, B_access_seq= reorder2.a_seq, reorder2.b_seq
    A_access_seq, B_access_seq, A_value_seq, B_value_seq= reorder1.intersection(A_sparse, A_sparse_csc)
    print("\nIntersection Mode:")
    print("A_access_seq:", A_access_seq)
    print("B_access_seq:", B_access_seq)
    # print("A_value_seq:", A_value_seq)
    # print("B_value_seq:", B_value_seq)
    