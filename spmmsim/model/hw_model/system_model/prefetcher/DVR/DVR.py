import sys
sys.path.append("../")
# import math 


from ..SP.stride_prefetch import StridePrefetcher
from ..utils.ewma_loop_bound_detector import EWMALoopBoundDetectorGroup as LBD


class DVR:
    def __init__(self, lbd=True, vector_size=4, ewma_alpha=0.3, initial_bound=2):
        self.lbd = lbd # 如果为False就是每次直接用上次的边界，用于模拟IMP
        self.coeff = 4 # 假设每个元素 4 字节
        self.stride_prefetcher = StridePrefetcher()  # 使用步长预取器
        self.loop_bound_group = LBD(num_detectors=vector_size, alpha=ewma_alpha, initial_bound=initial_bound)  # 基于EWMA 的循环边界检测器
    
    def stride_detector(self, curr_i):
        """步长检测器：使用传入的 StridePrefetcher 来预测下一个i值"""
        predicted_i, stride = self.stride_prefetcher.execute_mvin(curr_i)
        print(f"当前 i={curr_i}, 预测的下一个为 i={predicted_i}, 步长: {stride}")
        return predicted_i

    def loop_bound_detector(self, bound):
        """边界检测器"""
        # updated_bound = self.loop_bound_prefetcher.update(bound)
        updated_bounds = self.loop_bound_group.update_group(bound)
        return updated_bounds
    
    def addr_generator(self, base_ptr, col_add):
        """ 地址生成器 """
        return base_ptr + col_add

    def prefetch(self, bound, ptr_vector):
        """bound和ptr_vector都是PE行数相同的数组, bound[i]表示PE第i行的循环边界
        整合 stride_detector, loop_bound_detector, addr_generator
        """
        predicted_bounds = self.loop_bound_detector(bound)
        # print(predicted_bounds)
        
        # if self.lbd:
        #     for (detector_id, _, bound) in predicted_bounds:
        #         predicted_bounds = bound
            # print(bound)

        results = []
        # 对每个PE内处理
        for (detector_id, _, predicted_bound) in predicted_bounds:
            # for row in range(detector_id):
                # print(predicted_bounds[row])
                # print(predicted_bounds)
                # print(f"第{detector_id}行起始地址{ptr_vector[detector_id]}, 预测边界{round(bound)}")
            if self.lbd == False:
                predicted_bound = bound[detector_id]
            for col in range(round(predicted_bound)):
                predicted_addr = self.addr_generator(ptr_vector[detector_id], col)
                results.append((detector_id, predicted_addr))
                # PE第几行的CSR第几个数
                
        return results


if __name__ == "__main__":
    bound = [
        [2, 4, 5, 1],
        [2, 3, 4, 3],
        [3, 4, 2, 3],
    ]  
    ptr_vector = [
        [0, 0, 0, 0],
        [2, 5, 6, 2],
        [4, 8, 7, 5]
    ] 

    dvr = DVR(vector_size=4, ewma_alpha=0.3, initial_bound=2)

    for i in range(len(bound)):
        predict_addr = dvr.prefetch(bound[i], ptr_vector[i])
        print(f"第{i}轮生成的mem access{predict_addr}")
    