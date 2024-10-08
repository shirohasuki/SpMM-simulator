from sparse_unit import SparseUnit 
from sparse_format import SparseRepresentFormat
from sparse_align import SparseAlign
from sparse_addr_convert import SparseAddrConvert
from sparse_skip import SparseSkip
from sparse_tile import SparseTile
from utils.sparse_matrix import SparseMatrix
import numpy as np

# 连接内存的总线
def sparse_mem_access_pattern(A_matrix, B_matrix, is_one_side_sparsity, \
                              align_strategy, skip_strategy, tile_strategy, systolic_size, \
                                A_vector_addr, B_vector_addr, A_log_file, B_log_file):
    
    A_PE_tile_array, B_PE_tile_array = SparseUnit().sparse_access(sparse_matrix_a=A_matrix, 
        matrix_b=B_matrix, is_one_side_sparsity=is_one_side_sparsity, \
        align_strategy=align_strategy, skip_strategy=skip_strategy, tile_strategy=tile_strategy, \
        systolic_size=systolic_size)
    
    if ~is_one_side_sparsity:
        B_storage_strategy = "sparse"
        # B_PE_tile_array    = PE_tile_array_np
    else:
        B_storage_strategy = "dense"        
        # B_PE_tile_array    = PE_tile_array_coo
        
    A_access_msg = SparseAddrConvert("sparse", \
            A_PE_tile_array, A_vector_addr, vector_len=0, log_file=A_log_file).vaddr_msg
    B_access_msg = SparseAddrConvert(B_storage_strategy, \
            B_PE_tile_array, B_vector_addr, vector_len=0, log_file=B_log_file).vaddr_msg
    
    return A_access_msg, B_access_msg


# 连接计算单元的总线(buffer to 脉动阵列)
# def sparse_compute_input_seq(A_matrix, B_matrix, ):
    

#     A_value_seq = 0
#     B_value_seq = 0
#     return A_value_seq, B_value_seq



if __name__ == '__main__':
    A_sparse = SparseMatrix(2048, 2048, 1/16).matrix
    csr_A_sparse = SparseRepresentFormat(A_sparse, 'csr').sparse_matrix
    
    B_dense = np.random.randint(0, 10, size=(128, 2048))
    
    B_sparse = SparseMatrix(2048, 2048, 1/16).matrix
    csc_B_sparse = SparseRepresentFormat(B_sparse, 'csc').sparse_matrix




    # print("[TEST1][one-side-sparse, indirection, col_dim_skip, horizontal_tile, 16x16] \n")
    # A_access_msg, B_access_msg = sparse_mem_access_pattern(A_matrix=csr_A_sparse, 
    #                 B_matrix=B_dense, is_one_side_sparsity=True, \
    #                 align_strategy="indirection", skip_strategy="col_dim", tile_strategy="horizontal", \
    #                 systolic_size=(16, 16), A_vector_addr=False, B_vector_addr=True, \
    #                 A_log_file="./output/TEST1_A_access.txt", B_log_file="./output/TEST1_B_access.txt")
    
    print("[TEST2][two-side-sparse, intersection, OoO_skip, vertical_tile, 1x64] \n")
    A_access_msg, B_access_msg = sparse_mem_access_pattern(A_matrix=csr_A_sparse, 
                    B_matrix=csc_B_sparse, is_one_side_sparsity=False, \
                    align_strategy="intersection", skip_strategy="OoO", tile_strategy="vertical", \
                    systolic_size=(64, 1), A_vector_addr=False, B_vector_addr=False, \
                    A_log_file="./output/TEST2_A_access.txt", B_log_file="./output/TEST2_B_access.txt")
