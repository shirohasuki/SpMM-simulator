# 得到相对于矩阵起始点的位置
    
from collections import deque
import numpy as np

class SparseAddrConvert:
    def __init__(self, storage_strategy, PE_tile_array, vector_addr, vector_len, log_file):
        #
        # 输入 PE_tile_array
        # 输出最终访存序列
        #         
        # self.storage_strategy_map = {
        #     "dense": self.dense_storage_addr(PE_tile_array, vector_addr, vector_len), 
        #     "sparse": self.sparse_storage_addr(PE_tile_array, vector_addr, vector_len), 
        # } # map字典

        # if storage_strategy not in self.storage_strategy_map:
        #     raise ValueError(f"Unknown strategy: {storage_strategy}")
        if (storage_strategy == "sparse"):
            self.vaddr_msg = self.sparse_storage_addr(PE_tile_array, vector_addr, vector_len)
        elif (storage_strategy == "dense"):
            self.vaddr_msg = self.dense_storage_addr(PE_tile_array, vector_addr, vector_len)
        else:
            self.vaddr_msg=0
                    
        if log_file:
            np.set_printoptions(threshold=np.inf)
            with open(log_file, "w") as f:
                # print(self.vaddr_msg)
                for block_row_id, pe_id, addrs in self.vaddr_msg:
                    line = f"[block_row_id: {block_row_id}, PE_id: {pe_id}], [vector_addr: {vector_addr}, vector_len: {vector_len}], [ "
                    line += ", ".join(map(str, addrs)) + " ]\n"
                    f.write(line)     
            np.set_printoptions(threshold=1000)
    

    def dense_storage_addr(self, PE_tile_array, vector_addr=False, vector_len=0):
        # print("in dense")
        access_msg = []
        PE_ID = 0
        for block_row_id, pe_id, tile_coo in PE_tile_array:
            cols = []
            for row, col, value in zip(tile_coo.row, tile_coo.col, tile_coo.data):
                if value == -1:
                    continue
                (row_i, col_i) = value
                cols.append((row_i, col_i))  # 只保存col_i
                # cols.append((row, col, row_i, col_i))  # 只保存col_i

            access_msg.append((block_row_id, PE_ID, cols))  # 返回元组
            PE_ID += 1
        return access_msg

    def sparse_storage_addr(self, PE_tile_array, vector_addr=False, vector_len=0):
        # print("in sparse")
        global_counter = 1  # 全局编码从 1 开始
        encoded_values = []  # 保存编码后的值和对应位置

        for block_row_id in range(max(block_row_id for block_row_id, _, _ in PE_tile_array) + 1):
            block_row_pes = [tile for row_id, pe_id, tile in PE_tile_array if row_id == block_row_id]
            if not block_row_pes:
                continue

            num_rows, num_cols = block_row_pes[0].shape

            # 遍历每个 tile
            for i in range(num_rows):
                for pe_id, tile in enumerate(block_row_pes):
                    for j in range(num_cols):
                        if tile[i][j] not in (0, -1):  # 检查非零且非-1
                            # print("here")
                            (row, col) = tile[i][j]
                            encoded_values.append((block_row_id, pe_id, row, col, global_counter))
                            global_counter += 1  

        block_row_pe_dict = {}
        for block_row_id, pe_id, row, col, access in encoded_values:
            if (block_row_id, pe_id) not in block_row_pe_dict:
                block_row_pe_dict[(block_row_id, pe_id)] = []
            block_row_pe_dict[(block_row_id, pe_id)].append(str((row, col, access)))  # 只保存 code

        access_msg = []
        PE_ID = 0
        # with open("./A_mem_access1.txt", "w") as f:
        for (block_row_id, pe_id), access in block_row_pe_dict.items():
            # f.write(f"[block_row_id: {block_row_id}, PE_id: {PE_ID}], " +  ", ".join(access) + "\n")
            access_msg.append((block_row_id, PE_ID, access))
            PE_ID += 1
            
        return access_msg
    