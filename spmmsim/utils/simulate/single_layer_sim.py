import os

import sys
sys.path.append("../../../")

from spmmsim.utils.config.architecture import architecture as arch
from spmmsim.utils.config.workload import workload 
from spmmsim.compute.operand_matrix import operand_matrix as opmat
from spmmsim.compute.systolic_compute_os import systolic_compute_os
from spmmsim.compute.systolic_compute_ws import systolic_compute_ws
from spmmsim.compute.systolic_compute_is import systolic_compute_is
from spmmsim.memory.double_buffered_scratchpad_mem import double_buffered_scratchpad as mem_dbsp


class single_layer_sim:
    def __init__(self):
        self.layer_id = 0
        self.workload = workload()
        self.config = arch()

        self.op_mat_obj = opmat()
        self.compute_system = systolic_compute_os()
        self.memory_system = mem_dbsp()

        self.verbose = True

        # Report items : Compute report
        self.total_cycles = 0
        self.stall_cycles = 0
        self.num_compute = 0
        self.num_mac_unit = 0
        self.overall_util = 0
        self.mapping_eff = 0
        self.compute_util = 0

        # Report items : BW report
        self.avg_abuffer_bw = 0
        self.avg_bbuffer_bw = 0
        self.avg_cbuffer_bw = 0
        self.avg_adram_bw = 0
        self.avg_bdram_bw = 0
        self.avg_cdram_bw = 0

        # Report items : Detailed Access report
        # ABuffer
        self.abuffer_start_cycle = 0
        self.abuffer_stop_cycle = 0
        self.abuffer_reads = 0
        
        # BBuffer
        self.bbuffer_start_cycle = 0
        self.bbuffer_stop_cycle = 0
        self.bbuffer_reads = 0

        # CBuffer
        self.cbuffer_start_cycle = 0
        self.cbuffer_stop_cycle = 0
        self.cbuffer_writes = 0

        # ADram
        self.adram_start_cycle = 0
        self.adram_stop_cycle = 0
        self.adram_reads = 0

        # BDram
        self.bdram_start_cycle = 0
        self.bdram_stop_cycle = 0
        self.bdram_reads = 0

        # CDram
        self.cdram_start_cycle = 0
        self.cdram_stop_cycle = 0
        self.cdram_writes = 0

        self.params_set_flag = False
        self.memory_system_ready_flag = False
        self.runs_ready = False
        self.report_items_ready = False

    def set_params(self,
                   layer_id=0,
                   config_obj=arch(), workload_obj=workload(),
                   verbose=True):

        self.layer_id = layer_id
        self.config = config_obj
        self.workload = workload_obj

        self.op_mat_obj.set_params(layer_id=self.layer_id,
                                   config_obj=self.config,
                                   workloadutil_obj=self.workload,
                                   )

        self.dataflow = self.config.get_dataflow()
        if self.dataflow == 'os':
            self.compute_system = systolic_compute_os()
        elif self.dataflow == 'ws':
            self.compute_system = systolic_compute_ws()
        elif self.dataflow == 'is':
            self.compute_system = systolic_compute_is()

        arr_dims = self.config.get_array_dims()
        self.num_mac_unit = arr_dims[0] * arr_dims[1]
        self.verbose = verbose

        self.params_set_flag = True

    # This communicates that the memory is being managed externally
    # And the class will not interfere with setting it up
    def set_memory_system(self, mem_sys_obj=mem_dbsp()):
        self.memory_system = mem_sys_obj
        self.memory_system_ready_flag = True

    def run(self):
        assert self.params_set_flag, 'Parameters are not set. Run set_params()'

        # 1. Setup and the get the demand from compute system

        # 1.1 Get the operand matrices 获取操作数矩阵
        _, a_op_mat = self.op_mat_obj.get_a_matrix()
        _, b_op_mat = self.op_mat_obj.get_b_matrix()
        _, c_op_mat = self.op_mat_obj.get_c_matrix()

        self.num_compute = self.workload.get_layer_num_c_px(self.layer_id) \
                           * self.workload.get_layer_window_size(self.layer_id)

        # 1.2 Get the prefetch matrices for both operands
        self.compute_system.set_params(config_obj=self.config,
                                       a_op_mat=a_op_mat,
                                       b_op_mat=b_op_mat,
                                       c_op_mat=c_op_mat)

        # 1.3 Get the no compute demand matrices from for 2 operands and the output
        a_prefetch_mat, b_prefetch_mat = self.compute_system.get_prefetch_matrices()
        a_demand_mat, b_demand_mat, c_demand_mat = self.compute_system.get_demand_matrices()
        #print('DEBUG: Compute operations done')
        # 2. Setup the memory system and run the demands through it to find any memory bottleneck and generate traces

        # 2.1 Setup the memory system if it was not setup externally
        if not self.memory_system_ready_flag:
            word_size = 1           # bytes, this can be incorporated in the config file
            active_buf_frac = 0.5   # This can be incorporated in the config as well

            a_buf_size_kb, b_buf_size_kb, c_buf_size_kb = self.config.get_mem_sizes()
            a_buf_size_bytes = 1024 * a_buf_size_kb
            b_buf_size_bytes = 1024 * b_buf_size_kb
            c_buf_size_bytes = 1024 * c_buf_size_kb

            a_backing_bw = 1
            b_backing_bw = 1
            c_backing_bw = 1
            estimate_bandwidth_mode = False
            if self.config.use_user_dram_bandwidth():
                bws = self.config.get_bandwidths_as_list()
                a_backing_bw = bws[0]
                b_backing_bw = bws[0]
                c_backing_bw = bws[0]

            else:
                dataflow = self.config.get_dataflow()
                arr_row, arr_col = self.config.get_array_dims()
                estimate_bandwidth_mode = True

                # The number 10 elems per cycle is arbitrary
                a_backing_bw = 10
                b_backing_bw = 10
                c_backing_bw = arr_col

            # setting memory system
            self.memory_system.set_params(word_size                 = word_size,
                                          a_buf_size_bytes      = a_buf_size_bytes,
                                          b_buf_size_bytes     = b_buf_size_bytes,
                                          c_buf_size_bytes      = c_buf_size_bytes,
                                          rd_buf_active_frac        = active_buf_frac, 
                                          wr_buf_active_frac        = active_buf_frac,
                                          a_backing_buf_bw      = a_backing_bw,
                                          b_backing_buf_bw     = b_backing_bw,
                                          c_backing_buf_bw      = c_backing_bw,
                                          verbose                   = self.verbose,
                                          estimate_bandwidth_mode   = estimate_bandwidth_mode
            )

        # 2.2 Install the prefetch matrices to the read buffers to finish setup
        if self.config.use_user_dram_bandwidth() :
            self.memory_system.set_read_buf_prefetch_matrices(a_prefetch_mat=a_prefetch_mat,
                                                              b_prefetch_mat=b_prefetch_mat)

        # 2.3 Start sending the requests through the memory system until
        # all the c memory requests have been serviced
        self.memory_system.service_memory_requests(a_demand_mat, b_demand_mat, c_demand_mat)

        self.runs_ready = True

    # This will write the traces
    # def save_traces(self, top_path):
    #     assert self.params_set_flag, 'Parameters are not set'

    #     dir_name = top_path + '/layer' + str(self.layer_id)
    #     if not os.path.isdir(dir_name):
    #         os.mkdir(dir_name)

    #     abuffer_filename = dir_name +  '/abuffer_TRACE.csv'
    #     bbuffer_filename = dir_name + '/bbuffer_TRACE.csv'
    #     cbuffer_filename = dir_name +  '/cbuffer_TRACE.csv'

    #     adram_filename = dir_name +  '/adram_TRACE.csv'
    #     bdram_filename = dir_name + '/bdram_TRACE.csv'
    #     cdram_filename = dir_name +  '/cdram_TRACE.csv'

    #     self.memory_system.print_abuffer_trace(abuffer_filename)
    #     self.memory_system.print_adram_trace(adram_filename)
    #     self.memory_system.print_bbuffer_trace(bbuffer_filename)
    #     self.memory_system.print_bdram_trace(bdram_filename)
    #     self.memory_system.print_cbuffer_trace(cbuffer_filename)
    #     self.memory_system.print_cdram_trace(cdram_filename)

    #
    # def calc_report_data(self):
    #     assert self.runs_ready, 'Runs are not done yet'

    #     # Compute report
    #     self.total_cycles = self.memory_system.get_total_compute_cycles()
    #     self.stall_cycles = self.memory_system.get_stall_cycles()
    #     self.overall_util = (self.num_compute * 100) / (self.total_cycles * self.num_mac_unit)
    #     self.mapping_eff = self.compute_system.get_avg_mapping_efficiency() * 100
    #     self.compute_util = self.compute_system.get_avg_compute_utilization() * 100

    #     # BW report
    #     self.abuffer_reads = self.compute_system.get_a_requests()
    #     self.bbuffer_reads = self.compute_system.get_b_requests()
    #     self.cbuffer_writes = self.compute_system.get_c_requests()
    #     self.avg_abuffer_bw = self.abuffer_reads / self.total_cycles
    #     self.avg_bbuffer_bw = self.bbuffer_reads / self.total_cycles
    #     self.avg_cbuffer_bw = self.cbuffer_writes / self.total_cycles

    #     # Detail report
    #     self.abuffer_start_cycle, self.abuffer_stop_cycle \
    #         = self.memory_system.get_abuffer_start_stop_cycles()

    #     self.bbuffer_start_cycle, self.bbuffer_stop_cycle \
    #         = self.memory_system.get_bbuffer_start_stop_cycles()

    #     self.cbuffer_start_cycle, self.cbuffer_stop_cycle \
    #         = self.memory_system.get_cbuffer_start_stop_cycles()

    #     self.adram_start_cycle, self.adram_stop_cycle, self.adram_reads \
    #         = self.memory_system.get_adram_details()

    #     self.bdram_start_cycle, self.bdram_stop_cycle, self.bdram_reads \
    #         = self.memory_system.get_bdram_details()

    #     self.cdram_start_cycle, self.cdram_stop_cycle, self.cdram_writes \
    #         = self.memory_system.get_cdram_details()

    #     # BW calc for DRAM access
    #     self.avg_adram_bw = self.adram_reads / (self.adram_stop_cycle - self.adram_start_cycle + 1)
    #     self.avg_bdram_bw = self.bdram_reads / (self.bdram_stop_cycle - self.bdram_start_cycle + 1)
    #     self.avg_cdram_bw = self.cdram_writes / (self.cdram_stop_cycle - self.cdram_start_cycle + 1)

    #     self.report_items_ready = True

    # #
    # def get_layer_id(self):
    #     assert self.params_set_flag, 'Parameters are not set yet'
    #     return self.layer_id

    # #
    # def get_compute_report_items(self):
    #     if not self.report_items_ready:
    #         self.calc_report_data()

    #     items = [self.total_cycles, self.stall_cycles, self.overall_util, self.mapping_eff, self.compute_util]
    #     return items

    # #
    # def get_bandwidth_report_items(self):
    #     if not self.report_items_ready:
    #         self.calc_report_data()

    #     items = [self.avg_abuffer_bw, self.avg_bbuffer_bw, self.avg_cbuffer_bw]
    #     items += [self.avg_adram_bw, self.avg_bdram_bw, self.avg_cdram_bw]

    #     return items

    # #
    # def get_detail_report_items(self):
    #     if not self.report_items_ready:
    #         self.calc_report_data()

    #     items = [self.abuffer_start_cycle, self.abuffer_stop_cycle, self.abuffer_reads]
    #     items += [self.bbuffer_start_cycle, self.bbuffer_stop_cycle, self.bbuffer_reads]
    #     items += [self.cbuffer_start_cycle, self.cbuffer_stop_cycle, self.cbuffer_writes]
    #     items += [self.adram_start_cycle, self.adram_stop_cycle, self.adram_reads]
    #     items += [self.bdram_start_cycle, self.bdram_stop_cycle, self.bdram_reads]
    #     items += [self.cdram_start_cycle, self.cdram_stop_cycle, self.cdram_writes]

    #     return items
