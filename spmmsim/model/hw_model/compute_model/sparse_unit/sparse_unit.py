from format import SparseRepresentFormat
from sparse_align import SparseAlign
from sparse_addr_convert import SparseAddrConvert
from sparse_skip import SparseSkip
from sparse_tile import SparseTile


from utils.sparse_matrix import SparseMatrix
from scipy.sparse import coo_matrix

import numpy as np


class SparseUnit: 
    def __init__(self, ):
        self.a = 0
    

 
    def sparse_access(self, sparse_matrix_a, matrix_b, one_side_sparsity, 
            align_strategy, skip_strategy, tile_strategy,
            systolic_size=(16, 16)):

        A_access_msg = []
        B_access_msg = []

        # =============================================================================        
        # align: 稀疏对齐，获得初始访存矩阵
        # 输入原始矩阵(numpy)
        align = SparseAlign(sparse_matrix_a, matrix_b, A_sparsity=True, \
                                 B_sparsity=~one_side_sparsity, mode=align_strategy)
        
        a_align_access, b_align_access = align.a_seq, align.b_seq
        # 返回COO格式的序列
        
        # with open("./a_align_access.txt", "w") as f:
        #     for r, c, v in zip(a_align_access.row, a_align_access.col, a_align_access.data):
        #         f.write(f"{r} {c} {v}\n")
        # with open("./b_align_access.txt", "w") as f:
        #     for r, c, v in zip(b_align_access.row, b_align_access.col, b_align_access.data):
        #         f.write(f"{r} {c} {v}\n")
        # =============================================================================        
        # skip: 通过skip让计算与访存更紧凑
        systolic_row, systolic_col = systolic_size
        a_align_access_toarray = a_align_access.toarray()
        a_skip_matrix = np.zeros((a_align_access_toarray.shape), dtype=object)
        for i in range(0, a_align_access_toarray.shape[0], systolic_row):
            skip_block = SparseSkip( \
                coo_matrix(a_align_access_toarray[i:i+systolic_row]), skip_strategy=skip_strategy).skip_func
            if skip_block.shape[1] < 2048: # 如果当前列数小于 2048，则在右侧用 -1 填充到 2048 列
                skip_block = np.pad(skip_block, ((0, 0), (0, 2048 - skip_block.shape[1])), constant_values=-1)
            a_skip_matrix[i:i+systolic_row] = skip_block

        # =============================================================================        
        # tile: 不同平铺策略得到最终访存pattern
        # 输入 skip_matrix
        # 输出 PE_list[block_row/col_id, PE_id, PE_tile(COO格式/np.array格式)]
        PE_tile_array_coo = SparseTile(a_skip_matrix, tile_strategy="horizontal", systolic_size=systolic_size, coo_output=True).tile_func
        PE_tile_array_np = SparseTile(a_skip_matrix, tile_strategy="horizontal", systolic_size=systolic_size, coo_output=False).tile_func

        # np.set_printoptions(threshold=np.inf)
        # with open("./PE_tiles.txt", "w") as f:
        #     for block_row_id, pe_id, tile in PE_tile:
        #         tile_str = np.array2string(tile, separator=', ', max_line_width=np.inf)
        #         f.write(f"block_row_id: {block_row_id} PE_id: {pe_id}" + "\n" + tile_str + "\n\n")  # 加一个换行来分隔不同的 tiles
        # np.set_printoptions(threshold=1000)
        # ====================================================================
        # 地址格式转换，输出最终访存序列
        # 得到 B 访存序列
        B_access_msg = SparseAddrConvert(storage_strategy="dense", PE_tile_array=PE_tile_array_coo, \
            vector_addr=True, vector_len=0, log_file="./B_access_msg.txt").vaddr_msg

        # 得到 A 访存序列
        A_access_msg = SparseAddrConvert(storage_strategy="sparse", PE_tile_array=PE_tile_array_np, \
            vector_addr=False, vector_len=0, log_file="./A_access_msg.txt").vaddr_msg
    
        

        return A_access_msg, B_access_msg
    
    def padding():
        return 
        
        
    

    
if __name__ == '__main__':
    A_sparse = SparseMatrix(2048, 2048, 1/16).matrix
    csr_A_sparse = SparseRepresentFormat(A_sparse, 'csr').sparse_matrix
    B_dense = np.random.randint(0, 10, size=(128, 2048))
    
    A_access_msg, B_access_msg= SparseUnit().sparse_access(sparse_matrix_a=csr_A_sparse, 
        matrix_b=B_dense, one_side_sparsity=True, \
        align_strategy="indirection", skip_strategy="col_dim", tile_strategy="horizontal_tile", \
        systolic_size=(16, 16))

