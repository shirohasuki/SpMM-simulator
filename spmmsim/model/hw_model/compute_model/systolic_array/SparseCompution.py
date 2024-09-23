from spmmsim.model.hw_model.compute_model.systolic_array.SystolicArray import SystolicArray
from spmmsim.model.hw_model.compute_model.systolic_array.utils.IndexBuffer import IndexBuffer
import numpy as np

class SparseCompution:
    def __init__(self,buffer_row,buffer_col,systolic_col):
        self.buffer_row = buffer_row
        self.buffer_col = buffer_col
        self.systolic_col = systolic_col

        self.index_buffer   = IndexBuffer(row_num=buffer_row,col_num=buffer_col,systolic_col=systolic_col)
        self.systolic_array = SystolicArray(buffer_row, systolic_col)
        self.systolic_array.reset()



            

