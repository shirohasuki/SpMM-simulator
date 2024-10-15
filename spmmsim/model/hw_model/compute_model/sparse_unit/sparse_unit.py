from sparse_format import SparseRepresentFormat
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
    

 
    def sparse_access(self, sparse_matrix_a, matrix_b, is_one_side_sparsity, 
            align_strategy, skip_strategy, tile_strategy,
            systolic_size=(16, 16)):

        A_access_msg = []
        B_access_msg = []

        # =============================================================================        
        # align: 稀疏对齐，获得初始访存矩阵
        # 输入原始矩阵(numpy)
        align = SparseAlign(sparse_matrix_a, matrix_b, A_sparsity=True, \
                                B_sparsity=~is_one_side_sparsity, mode=align_strategy)
        
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
        # padding 后面单独加个函数
        # TODO: 这块单双边稀疏不同处理后面写到skip模块里面去
        systolic_row, systolic_col = systolic_size

        a_align_access_toarray = a_align_access.toarray()
        a_skip_matrix = np.zeros((a_align_access_toarray.shape), dtype=object)
        
        b_align_access_toarray = b_align_access.toarray()
        b_skip_matrix = np.zeros((b_align_access_toarray.shape), dtype=object)

        if is_one_side_sparsity: 
            for i in range(0, a_align_access_toarray.shape[0], systolic_row):
                skip_block = SparseSkip( \
                    coo_matrix(a_align_access_toarray[i:i+systolic_row]), skip_strategy=skip_strategy).skip_func
                if skip_block.shape[1] < 2048: # 如果当前列数小于 2048，则在右侧用 -1 填充到 2048 列
                    skip_block = np.pad(skip_block, ((0, 0), (0, 2048 - skip_block.shape[1])), constant_values=-1)
                a_skip_matrix[i:i+systolic_row] = skip_block
        else:
            for i in range(0, a_align_access_toarray.shape[1]):
                skip_block = SparseSkip( \
                    coo_matrix(a_align_access_toarray[:, i]), skip_strategy=skip_strategy).skip_func
                if skip_block.shape[0] < 2048: # 如果当前行数小于 2048，则在下侧用 -1 填充到 2048 行
                    skip_block = np.pad(skip_block, ((0, 0), (0, 2048 - skip_block.shape[0])), constant_values=-1)
                a_skip_matrix[:, i] = skip_block

            for i in range(0, b_align_access_toarray.shape[1]):
                skip_block = SparseSkip( \
                    coo_matrix(b_align_access_toarray[:, i]), skip_strategy=skip_strategy).skip_func
                if skip_block.shape[0] < 2048: # 如果当前行数小于 2048，则在下侧用 -1 填充到 2048 行
                    skip_block = np.pad(skip_block, ((0, 0), (0, 2048 - skip_block.shape[0])), constant_values=-1)
                a_skip_matrix[:, i] = skip_block


            # a_skip_matrix = SparseSkip(a_align_access, skip_strategy=skip_strategy).skip_func
            # b_skip_matrix = SparseSkip(b_align_access, skip_strategy=skip_strategy).skip_func
        
        # np.set_printoptions(threshold=np.inf)
        # with open("./a_skip_matrix.txt", "w") as f:
        #     for line in a_skip_matrix:
        #         f.write(f"{line}\n")
        # with open("./b_skip_matrix.txt", "w") as f:
        #     for line in b_skip_matrix:
        #         f.write(f"{line}\n")
        # np.set_printoptions(threshold=1000)
        # =============================================================================        
        # tile: 不同平铺策略得到最终访存pattern
        # 输入 skip_matrix
        # 输出 PE_list[block_row/col_id, PE_id, PE_tile(COO格式/np.array格式)]
        if is_one_side_sparsity:
            # B_PE_tile_array(coo) A_PE_tile_array(np)
            B_PE_tile_array = SparseTile(a_skip_matrix, tile_strategy=tile_strategy, systolic_size=systolic_size, coo_output=True).tile_func
            A_PE_tile_array = SparseTile(a_skip_matrix, tile_strategy=tile_strategy, systolic_size=systolic_size, coo_output=False).tile_func
        else: 
            # B_PE_tile_array(np) A_PE_tile_array(np)
            B_PE_tile_array = SparseTile(b_skip_matrix, tile_strategy=tile_strategy, systolic_size=systolic_size, coo_output=False).tile_func
            A_PE_tile_array = SparseTile(a_skip_matrix, tile_strategy=tile_strategy, systolic_size=systolic_size, coo_output=False).tile_func
        
        # np.set_printoptions(threshold=np.inf)
        # with open("./a_tile_matrix.txt", "w") as f:
        #     for line in A_PE_tile_array:
        #         f.write(f"{line}\n")
        # # with open("./b_tile_matrix.txt", "w") as f:
        # #     for line in B_PE_tile_array:
        # #         f.write(f"{line}\n")
        # with open("./b_tile_matrix.txt", "w") as f:
        #     for i, j, sparse_matrix in B_PE_tile_array:
        #         f.write(f"Tile ({i}, {j}):\n")
        #         # COO 格式的行、列和值
        #         row, col, data = sparse_matrix.row, sparse_matrix.col, sparse_matrix.data
        #         for r, c, v in zip(row, col, data):
        #             f.write(f"({r}, {c}) -> {v}\n")
        #         f.write("\n")
        # np.set_printoptions(threshold=1000)
        
        # ====================================================================
        # 地址格式转换，输出最终访存序列(测试时可打开)
        # 得到 B 访存序列
        # B_access_msg = SparseAddrConvert(storage_strategy="dense", PE_tile_array=PE_tile_array_coo, \
        #     vector_addr=True, vector_len=0, log_file="./output/B_access_msg.txt").vaddr_msg

        # # 得到 A 访存序列
        # A_access_msg = SparseAddrConvert(storage_strategy="sparse", PE_tile_array=PE_tile_array_np, \
        #     vector_addr=False, vector_len=0, log_file="./output/A_access_msg.txt").vaddr_msg
    
        return A_PE_tile_array, B_PE_tile_array
    
    def padding():
        return 
        
        
    

    
if __name__ == '__main__':
    A_sparse = SparseMatrix(2048, 2048, 1/16).matrix
    csr_A_sparse = SparseRepresentFormat(A_sparse, 'csr').sparse_matrix
    B_dense = np.random.randint(0, 10, size=(128, 2048))
    
    A_access_msg, B_access_msg= SparseUnit().sparse_access(sparse_matrix_a=csr_A_sparse, 
        matrix_b=B_dense, is_one_side_sparsity=True, \
        align_strategy="indirection", skip_strategy="col_dim", tile_strategy="horizontal_tile", \
        systolic_size=(16, 16))

