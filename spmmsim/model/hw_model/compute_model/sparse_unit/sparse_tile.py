from format import SparseRepresentFormat
from sparse_align import SparseAlign
from sparse_addr_convert import SparseAddrConvert
from sparse_skip import SparseSkip
from numpy.lib.stride_tricks import sliding_window_view
from scipy.sparse import coo_matrix

from utils.sparse_matrix import SparseMatrix

import numpy as np


class SparseTile: 
    def __init__(self, dense_matrix, tile_strategy, systolic_size, coo_output):
        # self.dense_matrix   = dense_matrix
        # self.tile_strategy  = tile_strategy
        # self.systolic_size  = systolic_size
        # self.coo_output     = coo_output
        
        self.tile_func_map = {
            "horizontal": self.horizontal_tile(dense_matrix, systolic_size, coo_output), 
            "vertical": self.vertical_tile(dense_matrix, systolic_size, coo_output), 
        } # map字典

        if tile_strategy not in self.tile_func_map:
            raise ValueError(f"Unknown strategy: {tile_strategy}")
        
        # 输入dense矩阵, 输出[block_row/col_id, PE_id, PE_tile(COO格式)]
        self.tile_func = self.tile_func_map[tile_strategy]
    
    def sliding_window(self, matrix, window_size=(16, 16)):
        rows, cols = matrix.shape

        # 计算需要填充的行和列，使得矩阵维度可以被window_size整除
        row_padding = (window_size[0] - rows % window_size[0]) % window_size[0]
        col_padding = (window_size[1] - cols % window_size[1]) % window_size[1]

        # 使用np.pad填充矩阵，填充为-1, 得到可以整除的矩阵
        padded_matrix = np.pad(matrix, 
                            ((0, row_padding), (0, col_padding)), 
                            mode='constant', constant_values=-1)

        tiled_matmul = sliding_window_view(padded_matrix, window_shape=window_size)
        return tiled_matmul
    
    # 左右左移动计算块(A跳跃, B连续)
    def horizontal_tile(self, dense_matrix, systol_size, coo_output):
        (systolic_row, systolic_col) = systol_size
        PE_tile_output = []

        for block_row_id in range(0, dense_matrix.shape[0], systolic_row):
            a_tiles = self.sliding_window(
                dense_matrix[block_row_id:block_row_id+systolic_row], window_size=systol_size)
            a_tiles = a_tiles[::systolic_col, ::systolic_col]  # 一行的PEs
            
            for pe_id, tile in enumerate(a_tiles[0]):
                if np.all(tile == -1):
                    break
                if coo_output:
                    tile = coo_matrix(tile)
                # print(type(tile))
                PE_tile_output.append((block_row_id, pe_id, tile))

        return PE_tile_output
    
    # 左右左移动计算块(A跳跃, B连续)
    # def horizontal_tile(self, dense_matrix, systol_size):
    #     block_row_id = 0
    #     PE_id = 0
    #     PE_tile = [] 
    #     (systolic_row, systolic_col) = systol_size
    #     for i in range(0, dense_matrix.shape[0], systolic_row):
    #         a_tiles = self.sliding_window(dense_matrix[i:i+systolic_row], window_size=systol_size)
    #         a_tiles = a_tiles[::systolic_col, ::systolic_col] # 一行的PEs
    #         for j in range(a_tiles.shape[1]):
    #             if np.all(a_tiles[0][j] == -1):
    #                 break
    #             else:
    #                 PE_tile.append((block_row_id, PE_id, a_tiles[0][j]))
    #                 PE_id += 1  
    #         block_row_id += 1

    #     PE_tile_coo = []
    #     for block_row_id, pe_id, tile in PE_tile:
    #         tile_coo = coo_matrix(tile)
    #         # 将 (block_row_id, pe_id, tile_coo) 存入 PE_tile_coo 列表
    #         PE_tile_coo.append((block_row_id, pe_id, tile_coo))
        
    #     return PE_tile_coo
    
    # 下上下移动计算块(A连续, B跳跃)
    def vertical_tile(self, dense_matrix, systol_size, coo_output):
        (systolic_row, systolic_col) = systol_size
        PE_tile_output = []

        for block_col_id in range(0, dense_matrix.shape[1], systolic_col):
            a_tiles = self.sliding_window(dense_matrix[:, block_col_id:block_col_id+systolic_col], window_size=systol_size)
            a_tiles = a_tiles[::systolic_row, ::systolic_row]  # 一列的PEs
            
            for pe_id, tile in enumerate(a_tiles[1]):
                if np.all(tile == -1):
                    break
                if coo_output:
                    tile = coo_matrix(tile)
                PE_tile_output.append((block_col_id, pe_id, tile))

        return PE_tile_output 
   
    
if __name__ == '__main__':
    dense_matrix = np.array([
        [1, 2, 3, 0, 0],
        [0, 4, 5, 6, 0],
        [7, 0, 0, 8, 9],
        [0, 10, 11, 0, 0]
    ])
    
    result1 = SparseTile(dense_matrix, "horizontal", (2, 2)).tile_func
    
    print("Horizontal Tile Result:")
    for item in result1:
        print(item)
    
    result2 = SparseTile(dense_matrix, "vertical", (2, 2)).tile_func 
    
    print("Vertical Tile Result:")
    for item in result2:
        print(item)
    

    
    
        
