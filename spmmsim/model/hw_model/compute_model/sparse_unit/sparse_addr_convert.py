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
                    # print(type(addrs))
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
                # print(row, col, row_i, col_i)
                cols.append((int(row_i), int(col_i)))  # 只保存col_i
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
            # block_row_pes = [tile for pe_id, tile in sorted(
            #     [(pe_id, tile) for row_id, pe_id, tile in PE_tile_array if row_id == block_row_id],
            #     key=lambda x: x[0]
            # )]

            # block_row_pes = sorted(
            #     [tile for row_id, pe_id, tile in PE_tile_array if row_id == block_row_id],
            #     key=lambda tile: next(pe_id for r, pe_id, t in PE_tile_array if t == tile)
            # )

            # block_row_pes = []
            # for row_id, pe_id, tile in PE_tile_array:
            import pdb
            #     if block_row_id == row_id:
            #         # print(tile)
            #         block_row_pes.append(tile)
            
            # print(block_row_pes)            
            # pdb.set_trace()

            if not block_row_pes:
                continue

            num_rows, num_cols = block_row_pes[0].shape
            # print(num_rows, num_cols)            

            # 遍历每个 tile
            for i in range(num_rows):
                for pe_id, tile in enumerate(block_row_pes):
                    for j in range(num_cols):
                        if tile[i][j] not in (0, -1):  # 检查非零且非-1
                            # print("here")
                            (row, col) = tile[i][j]
                            encoded_values.append((block_row_id, pe_id, int(row), int(col), global_counter))
                            global_counter += 1 
                            # print(pe_id, tile)            
                            # pdb.set_trace()

        # with open("./log.txt", "w") as f:
        #     for block_row_id, pe_id, row, col, access in encoded_values:
        #         line = f"[block_row_id: {block_row_id}, PE_id: {pe_id}], [row: {row}, col: {col}], [access: {access}]\n"
        #         f.write(line)

        block_row_pe_dict = {}
        for block_row_id, pe_id, row, col, access in encoded_values:
            if (block_row_id, pe_id) not in block_row_pe_dict:
                block_row_pe_dict[(block_row_id, pe_id)] = []
            block_row_pe_dict[(block_row_id, pe_id)].append(str((row, col, access)))  # 只保存 code

        # with open("./block_row_pe_dict.txt", "w") as f:
        #     for (block_row_id, pe_id), access in block_row_pe_dict.items():
        #         f.write(f"[block_row_id: {block_row_id}, PE_id: {pe_id}], " +  ", ".join(access) + "\n")

        access_msg = []
        # PE_ID = 0
        # with open("./A_mem_access1.txt", "w") as f:
        for (block_row_id, pe_id), access in block_row_pe_dict.items():
            # f.write(f"[block_row_id: {block_row_id}, PE_id: {PE_ID}], " +  ", ".join(access) + "\n")
            access_msg.append((block_row_id, pe_id, access))
            # PE_ID += 1
        
        access_msg = sorted(access_msg, key=lambda x: (x[0], x[1]))
        
        return access_msg
    
    # def sparse_storage_addr(self, PE_tile_array, vector_addr=False, vector_len=0):
    #     global_counter = 1  # 全局编码从 1 开始
    #     encoded_values = []  # 保存编码后的值和对应位置

    #     current_block_row_id = None
    #     block_row_pes = []

    #     for row_id, pe_id, tile in PE_tile_array:
    #         # 检查是否进入新的 block_row_id
    #         if row_id != current_block_row_id:
    #             # 如果进入新的 block_row_id，处理前一个 block_row_id 的块
    #             if block_row_pes:
    #                 num_rows, num_cols = block_row_pes[0][1].shape  # 获取当前块的尺寸

    #                 # 遍历当前 block_row_id 中的每个 tile
    #                 for i in range(num_rows):
    #                     for pe_id, tile in block_row_pes:
    #                         for j in range(num_cols):
    #                             if tile[i][j] not in (0, -1):  # 检查非零且非-1
    #                                 (row, col) = tile[i][j]
    #                                 encoded_values.append((current_block_row_id, pe_id, int(row), int(col), global_counter))
    #                                 global_counter += 1

    #             # 更新 current_block_row_id 并重置 block_row_pes
    #             current_block_row_id = row_id
    #             block_row_pes = []

    #         # 将当前 PE (Processing Element) 添加到当前的 block_row_pes
    #         block_row_pes.append((pe_id, tile))

    #     # 最后一个 block_row_id 的块需要在循环结束后再处理
    #     if block_row_pes:
    #         num_rows, num_cols = block_row_pes[0][1].shape
    #         for i in range(num_rows):
    #             for pe_id, tile in block_row_pes:
    #                 for j in range(num_cols):
    #                     if tile[i][j] not in (0, -1):
    #                         (row, col) = tile[i][j]
    #                         encoded_values.append((current_block_row_id, pe_id, int(row), int(col), global_counter))
    #                         global_counter += 1

    #     # 对 `encoded_values` 进行编码整理
    #     block_row_pe_dict = {}
    #     for block_row_id, pe_id, row, col, access in encoded_values:
    #         if (block_row_id, pe_id) not in block_row_pe_dict:
    #             block_row_pe_dict[(block_row_id, pe_id)] = []
    #         block_row_pe_dict[(block_row_id, pe_id)].append(str((row, col, access)))  # 只保存 code

    #     access_msg = []
    #     PE_ID = 0
    #     # with open("./A_mem_access1.txt", "w") as f:
    #     for (block_row_id, pe_id), access in block_row_pe_dict.items():
    #         # f.write(f"[block_row_id: {block_row_id}, PE_id: {PE_ID}], " +  ", ".join(access) + "\n")
    #         access_msg.append((block_row_id, PE_ID, access))
    #         PE_ID += 1

    #     return access_msg
