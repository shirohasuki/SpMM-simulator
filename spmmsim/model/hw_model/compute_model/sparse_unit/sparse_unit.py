# from format import SparseRepresentFormat
# from spmmsim.model.hw_model.compute_model.sparse_unit.sparse_align import SparseReorder
# from sparse_addr_convert import SparseAddrConvert
# from spmmsim.model.hw_model.compute_model.sparse_unit.sparse_skip import SparseAlign


# from utils.sparse_matrix import SparseMatrix

# import numpy as np


# class SparseUnit: 
#     def __init__(self, ):
#         self.a = 0
    

    # 左右左移动计算块(加载A行B列)
    # 原则，软件上永远密集矩阵操作，直到输出
    # def one_dim_skip(self, sparse_matrix_a, dense_matrix_b, systolic_row, systolic_col):

    #     A_skip_access_message_matrix=[]
    #     B_skip_access_message_matrix=[]

        
    #     return A_skip_access_message_matrix, B_skip_access_message_matrix, \
    #             A_buffer_matrix, B_buffer_matrix 
        # matrix_row, matrix_col = sparse_matrix_a.shape

        # # reorder: 得到哪些a和b参与运算
        # reorder = SparseReorder(sparse_matrix_a, dense_matrix_b, A_sparsity=True, 
        #                          B_sparsity=False, mode="indirection", return_seq="access")
        # A_access_seq, B_access_seq = reorder.a_seq, reorder.b_seq
        # # for i in range(len(A_access_seq[0])):
        # #     print(A_access_seq[0][i], end='')        

        # with open ("./A_access_seq.txt", "w") as f:
        #     for line in A_access_seq:
        #         f.write("[ " +", ".join(map(str, line)) + "]\n")
                
        # with open ("./B_access_seq.txt", "w") as f:
        #     for line in B_access_seq:
        #         f.write("[ " +", ".join(map(str, line)) + "]\n")
        # # ============================================================================
        # # 将稀疏矩阵转换为密集矩阵(处理矩阵)以便操作        
        # A_process_matrix = np.full([len(B_access_seq), 
        #                             len(max(B_access_seq, key = lambda x: len(x)))], fill_value=-1)
        # for i, j in enumerate(B_access_seq):
        #     A_process_matrix[i][0:len(j)] = j
        
        # # =============================================================================        
        # # align: 稀疏对齐，通过skip让计算更紧凑
        # tiled_matmul_a = []
        # align = SparseAlign()
        # # print(A_access_seq.type())
        # for i in range(0, len(A_process_matrix), 16):
        #     aligned_block = align.col_dim_align(A_process_matrix[i:i+16], 16, 2048) # 对齐
        #     # print(aligned_block)
        #     aligned_tiled = align.sliding_window(aligned_block, window_size=(16, 16))
        #     # 设置步长为 16，即每 16 步滑动一次
        #     aligned_tiled = aligned_tiled[::16, ::16]
        #     tiled_matmul_a.append(aligned_tiled) # 滑窗
        
        # np.set_printoptions(threshold=np.inf)
        # with open ("./tiled_matmul_a.txt", "w") as f:
        #     for line in tiled_matmul_a:
        #         line_str = np.array2string(line, separator=', ', max_line_width=np.inf)
        #         f.write(line_str + "\n")  # 将每一行写入文件，手动换行
        # np.set_printoptions(threshold=1000)
        
        # # ============================================================================= 
        # # 生成对齐后以计算tile为单元的访存序列        
        # A_access_seq_tiled, B_access_seq_tiled = align.aligned_access(tiled_matmul_a, B_access_seq)
        # # print(B_access_seq)
        # # ============================================================================= 
        # # generate skip access message matrix
        # A_skip_access_message_matrix=[]
        # B_skip_access_message_matrix=[]
        # skip_access_matrix=[]
        # # import pdb

        # # for (row_block_id, PE_id, tile_a) in A_access_seq_tiled:
        # #     print(A_access_seq[row_block_id*16:(row_block_id+1)*16], tile_a)
            
        # #     updated_matrix1, popped_elements = \
        # #         SparseAddrConvert(sparse_matrix_a.shape[0], sparse_matrix_a.shape[1]).addr_convert_deque( \
        # #         A_access_seq[row_block_id*16:(row_block_id+1)*16], tile_a)
            
        # #     skip_access_matrix.append(popped_elements)
        
        # # SparseAddrConvert(sparse_matrix_a.shape[0], sparse_matrix_a.shape[1]).skip_message(\
        # #         self, skip_access_matrix, vector_addr=False, vector_size=0)

        # # pdb.set_trace()

        # # B_access_seq[0] PE_id [1] tile_b
        # # 提取每个元组的第二个元素(tile_b)组成新列表
        # tile_b_list = [item[1] for item in B_access_seq_tiled]
        # # print(tile_b_list)
        # B_skip_access_message_matrix.append(SparseAddrConvert(dense_matrix_b.shape[0], 
        #         dense_matrix_b.shape[1]).gate_to_skip_message(tile_b_list, vector_addr=True, vector_size=16))
        # B_skip_access_message_matrix

        # with open ("./A_skip_access_message_matrix.txt", "w") as f:
        #     for line in A_skip_access_message_matrix:
        #         # line_str = np.array2string(line[1], separator=', ', max_line_width=np.inf)
        #         f.write(str(line) + "\n")
                
        #         # import pdb
        # with open ("./B_skip_access_message_matrix.txt", "w") as f:
        #     for line in B_skip_access_message_matrix[0]:
        #         # pdb.set_trace()
        #         # print(line[1].tolist())
        #         # line_str = np.array2string(line[1], separator=', ', max_line_width=np.inf)
        #         f.write("(" + str(line[0]) + ", " + str(line[1].tolist()) + ", " + str(line[2]) + ")" + "\n")
        

        # A_buffer_matrix = []
        # B_buffer_matrix = []
        # return A_skip_access_message_matrix, B_skip_access_message_matrix, \
        #         A_buffer_matrix, B_buffer_matrix
    

    # def two_dim_skip(self, sparse_matrix_a, sparse_matrix_b):
        
    #     return 
    
# if __name__ == '__main__':
#     A_sparse = SparseMatrix(2048, 2048, 1/16).matrix
#     # for i in A_sparse[0]:
#         # print(A_sparse[0][i], end='')
#     csr_A_sparse = SparseRepresentFormat(A_sparse, 'csr').sparse_matrix
#     # print(csr_A_sparse.sparse_matrix)
#     B_dense = np.random.randint(0, 10, size=(128, 2048))
    
#     A_mem_memssage, B_mem_memssage, A_buffer_matrix, B_buffer_matrix = SparseUnit().one_dim_skip(sparse_matrix_a=csr_A_sparse, 
#         dense_matrix_b=B_dense, systolic_row=16, systolic_col=16)
    
    
        
