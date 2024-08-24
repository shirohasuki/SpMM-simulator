import time
import numpy as np
from tqdm import tqdm

from utils.read_buffer import read_buffer as rdbuf
from utils.read_buffer_estimate_bw import ReadBufferEstimateBw as rdbuf_est
from utils.read_port import read_port as rdport
from utils.write_buffer import write_buffer as wrbuf
from utils.write_port import write_port as wrport


class double_buffered_scratchpad:
    def __init__(self):
        self.ifmap_buf = rdbuf()
        self.filter_buf = rdbuf()
        self.ofmap_buf =wrbuf()

        self.ifmap_port = rdport()
        self.filter_port = rdport()
        self.ofmap_port = wrport()

        self.verbose = True

        self.ifmap_trace_matrix = np.zeros((1,1), dtype=int)
        self.filter_trace_matrix = np.zeros((1,1), dtype=int)
        self.ofmap_trace_matrix = np.zeros((1,1), dtype=int)

        # Metrics to gather for generating run reports
        self.total_cycles = 0
        self.compute_cycles = 0
        self.stall_cycles = 0

        self.avg_ifmap_dram_bw = 0
        self.avg_filter_dram_bw = 0
        self.avg_ofmap_dram_bw = 0

        self.ifmap_sram_start_cycle = 0
        self.ifmap_sram_stop_cycle = 0
        self.filter_sram_start_cycle = 0
        self.filter_sram_stop_cycle = 0
        self.ofmap_sram_start_cycle = 0
        self.ofmap_sram_stop_cycle = 0

        self.ifmap_dram_start_cycle = 0
        self.ifmap_dram_stop_cycle = 0
        self.ifmap_dram_reads = 0
        self.filter_dram_start_cycle = 0
        self.filter_dram_stop_cycle = 0
        self.filter_dram_reads = 0
        self.ofmap_dram_start_cycle = 0
        self.ofmap_dram_stop_cycle = 0
        self.ofmap_dram_writes = 0

        self.estimate_bandwidth_mode = False,
        self.traces_valid = False
        self.params_valid_flag = True

    #
    def set_params(self,
                   verbose=True,
                   estimate_bandwidth_mode=False,
                   word_size=1,
                   ifmap_buf_size_bytes=2, filter_buf_size_bytes=2, ofmap_buf_size_bytes=2,
                   rd_buf_active_frac=0.5, wr_buf_active_frac=0.5,
                   ifmap_backing_buf_bw=1, filter_backing_buf_bw=1, ofmap_backing_buf_bw=1):

        self.estimate_bandwidth_mode = estimate_bandwidth_mode

        if self.estimate_bandwidth_mode:
            self.ifmap_buf = rdbuf_est()
            self.filter_buf = rdbuf_est()

            self.ifmap_buf.set_params(backing_buf_obj=self.ifmap_port,
                                      total_size_bytes=ifmap_buf_size_bytes,
                                      word_size=word_size,
                                      active_buf_frac=rd_buf_active_frac,
                                      backing_buf_default_bw=ifmap_backing_buf_bw)

            self.filter_buf.set_params(backing_buf_obj=self.filter_port,
                                       total_size_bytes=filter_buf_size_bytes,
                                       word_size=word_size,
                                       active_buf_frac=rd_buf_active_frac,
                                       backing_buf_default_bw=filter_backing_buf_bw)
        else:
            self.ifmap_buf = rdbuf()
            self.filter_buf = rdbuf()

            self.ifmap_buf.set_params(backing_buf_obj=self.ifmap_port,
                                      total_size_bytes=ifmap_buf_size_bytes,
                                      word_size=word_size,
                                      active_buf_frac=rd_buf_active_frac,
                                      backing_buf_bw=ifmap_backing_buf_bw)

            self.filter_buf.set_params(backing_buf_obj=self.filter_port,
                                       total_size_bytes=filter_buf_size_bytes,
                                       word_size=word_size,
                                       active_buf_frac=rd_buf_active_frac,
                                       backing_buf_bw=filter_backing_buf_bw)

        self.ofmap_buf.set_params(backing_buf_obj=self.ofmap_port,
                                  total_size_bytes=ofmap_buf_size_bytes,
                                  word_size=word_size,
                                  active_buf_frac=wr_buf_active_frac,
                                  backing_buf_bw=ofmap_backing_buf_bw)

        self.verbose = verbose

        self.params_valid_flag = True

    #
    def set_read_buf_prefetch_matrices(self,
                                       ifmap_prefetch_mat=np.zeros((1,1)),
                                       filter_prefetch_mat=np.zeros((1,1))
                                       ):

        self.ifmap_buf.set_fetch_matrix(ifmap_prefetch_mat)
        self.filter_buf.set_fetch_matrix(filter_prefetch_mat)

    #
    def reset_buffer_states(self):

        self.ifmap_buf.reset()
        self.filter_buf.reset()
        self.ofmap_buf.reset()

    # The following are just shell methods for users to control each mem individually
    def service_ifmap_reads(self,
                            incoming_requests_arr_np,   # 2D array with the requests
                            incoming_cycles_arr):
        out_cycles_arr_np = self.ifmap_buf.service_reads(incoming_requests_arr_np, incoming_cycles_arr)

        return out_cycles_arr_np

    #
    def service_filter_reads(self,
                            incoming_requests_arr_np,   # 2D array with the requests
                            incoming_cycles_arr):
        out_cycles_arr_np = self.filter_buf.service_reads(incoming_requests_arr_np, incoming_cycles_arr)

        return out_cycles_arr_np

    #
    def service_ofmap_writes(self,
                             incoming_requests_arr_np,  # 2D array with the requests
                             incoming_cycles_arr):

        out_cycles_arr_np = self.ofmap_buf.service_writes(incoming_requests_arr_np, incoming_cycles_arr)

        return out_cycles_arr_np

    #
    def service_memory_requests(self, ifmap_demand_mat, filter_demand_mat, ofmap_demand_mat):
        assert self.params_valid_flag, 'Memories not initialized yet'

        ofmap_lines = ofmap_demand_mat.shape[0]

        self.total_cycles = 0
        self.stall_cycles = 0

        ifmap_hit_latency = self.ifmap_buf.get_hit_latency()
        filter_hit_latency = self.filter_buf.get_hit_latency()

        ifmap_serviced_cycles = []
        filter_serviced_cycles = []
        ofmap_serviced_cycles = []

        pbar_disable = not self.verbose
        for i in tqdm(range(ofmap_lines), disable=pbar_disable):

            cycle_arr = np.zeros((1,1)) + i + self.stall_cycles

            ifmap_demand_line = ifmap_demand_mat[i, :].reshape((1,ifmap_demand_mat.shape[1]))
            ifmap_cycle_out = self.ifmap_buf.service_reads(incoming_requests_arr_np=ifmap_demand_line,
                                                            incoming_cycles_arr=cycle_arr)
            ifmap_serviced_cycles += [ifmap_cycle_out[0]]
            ifmap_stalls = ifmap_cycle_out[0] - cycle_arr[0] - ifmap_hit_latency

            filter_demand_line = filter_demand_mat[i, :].reshape((1, filter_demand_mat.shape[1]))
            filter_cycle_out = self.filter_buf.service_reads(incoming_requests_arr_np=filter_demand_line,
                                                           incoming_cycles_arr=cycle_arr)
            filter_serviced_cycles += [filter_cycle_out[0]]
            filter_stalls = filter_cycle_out[0] - cycle_arr[0] - filter_hit_latency

            ofmap_demand_line = ofmap_demand_mat[i, :].reshape((1, ofmap_demand_mat.shape[1]))
            ofmap_cycle_out = self.ofmap_buf.service_writes(incoming_requests_arr_np=ofmap_demand_line,
                                                             incoming_cycles_arr_np=cycle_arr)
            ofmap_serviced_cycles += [ofmap_cycle_out[0]]
            ofmap_stalls = ofmap_cycle_out[0] - cycle_arr[0] - 1

            self.stall_cycles += int(max(ifmap_stalls[0], filter_stalls[0], ofmap_stalls[0]))

        if self.estimate_bandwidth_mode:
            # IDE shows warning as complete_all_prefetches is not implemented in read_buffer class
            # It is harmless since, in estimate bandwidth mode, read_buffer_estimate_bw is instantiated
            self.ifmap_buf.complete_all_prefetches()
            self.filter_buf.complete_all_prefetches()

        self.ofmap_buf.empty_all_buffers(ofmap_serviced_cycles[-1])

        # Prepare the traces
        ifmap_services_cycles_np = np.asarray(ifmap_serviced_cycles).reshape((len(ifmap_serviced_cycles), 1))
        self.ifmap_trace_matrix = np.concatenate((ifmap_services_cycles_np, ifmap_demand_mat), axis=1)

        filter_services_cycles_np = np.asarray(filter_serviced_cycles).reshape((len(filter_serviced_cycles), 1))
        self.filter_trace_matrix = np.concatenate((filter_services_cycles_np, filter_demand_mat), axis=1)

        ofmap_services_cycles_np = np.asarray(ofmap_serviced_cycles).reshape((len(ofmap_serviced_cycles), 1))
        self.ofmap_trace_matrix = np.concatenate((ofmap_services_cycles_np, ofmap_demand_mat), axis=1)
        self.total_cycles = int(ofmap_serviced_cycles[-1][0])

        # END of serving demands from memory
        self.traces_valid = True

    #
    def get_total_compute_cycles(self):
        assert self.traces_valid, 'Traces not generated yet'
        return self.total_cycles

    #
    def get_stall_cycles(self):
        assert self.traces_valid, 'Traces not generated yet'
        return self.stall_cycles

    #
    def get_ifmap_sram_start_stop_cycles(self):
        assert self.traces_valid, 'Traces not generated yet'

        done = False
        for ridx in range(self.ifmap_trace_matrix.shape[0]):
            if done:
                break
            row = self.ifmap_trace_matrix[ridx,1:]
            for addr in row:
                if not addr == -1:
                    self.ifmap_sram_start_cycle = self.ifmap_trace_matrix[ridx][0]
                    done = True
                    break

        done = False
        for ridx in range(self.ifmap_trace_matrix.shape[0]):
            if done:
                break
            ridx = -1 * (ridx + 1)
            row = self.ifmap_trace_matrix[ridx,1:]
            for addr in row:
                if not addr == -1:
                    self.ifmap_sram_stop_cycle  = self.ifmap_trace_matrix[ridx][0]
                    done = True
                    break

        return self.ifmap_sram_start_cycle, self.ifmap_sram_stop_cycle

    #
    def get_filter_sram_start_stop_cycles(self):
        assert self.traces_valid, 'Traces not generated yet'

        done = False
        for ridx in range(self.filter_trace_matrix.shape[0]):
            if done:
                break
            row = self.filter_trace_matrix[ridx, 1:]
            for addr in row:
                if not addr == -1:
                    self.filter_sram_start_cycle = self.filter_trace_matrix[ridx][0]
                    done = True
                    break

        done = False
        for ridx in range(self.filter_trace_matrix.shape[0]):
            if done:
                break
            ridx = -1 * (ridx + 1)
            row = self.filter_trace_matrix[ridx, 1:]
            for addr in row:
                if not addr == -1:
                    self.filter_sram_stop_cycle = self.filter_trace_matrix[ridx][0]
                    done = True
                    break

        return self.filter_sram_start_cycle, self.filter_sram_stop_cycle

    #
    def get_ofmap_sram_start_stop_cycles(self):
        assert self.traces_valid, 'Traces not generated yet'

        done = False
        for ridx in range(self.ofmap_trace_matrix.shape[0]):
            if done:
                break
            row = self.ofmap_trace_matrix[ridx, 1:]
            for addr in row:
                if not addr == -1:
                    self.ofmap_sram_start_cycle = self.ofmap_trace_matrix[ridx][0]
                    done = True
                    break

        done = False
        for ridx in range(self.ofmap_trace_matrix.shape[0]):
            if done:
                break
            ridx = -1 * (ridx + 1)
            row = self.ofmap_trace_matrix[ridx, 1:]
            for addr in row:
                if not addr == -1:
                    self.ofmap_sram_stop_cycle = self.ofmap_trace_matrix[ridx][0]
                    done = True
                    break

        return self.ofmap_sram_start_cycle, self.ofmap_sram_stop_cycle

    #
    def get_ifmap_dram_details(self):
        assert self.traces_valid, 'Traces not generated yet'

        self.ifmap_dram_reads = self.ifmap_buf.get_num_accesses()
        self.ifmap_dram_start_cycle, self.ifmap_dram_stop_cycle \
            = self.ifmap_buf.get_external_access_start_stop_cycles()

        return self.ifmap_dram_start_cycle, self.ifmap_dram_stop_cycle, self.ifmap_dram_reads

    #
    def get_filter_dram_details(self):
        assert self.traces_valid, 'Traces not generated yet'

        self.filter_dram_reads = self.filter_buf.get_num_accesses()
        self.filter_dram_start_cycle, self.filter_dram_stop_cycle \
            = self.filter_buf.get_external_access_start_stop_cycles()

        return self.filter_dram_start_cycle, self.filter_dram_stop_cycle, self.filter_dram_reads

    #
    def get_ofmap_dram_details(self):
        assert self.traces_valid, 'Traces not generated yet'

        self.ofmap_dram_writes = self.ofmap_buf.get_num_accesses()
        self.ofmap_dram_start_cycle, self.ofmap_dram_stop_cycle \
            = self.ofmap_buf.get_external_access_start_stop_cycles()

        return self.ofmap_dram_start_cycle, self.ofmap_dram_stop_cycle, self.ofmap_dram_writes

    #
    def get_ifmap_sram_trace_matrix(self):
        assert self.traces_valid, 'Traces not generated yet'
        return self.ifmap_trace_matrix

    #
    def get_filter_sram_trace_matrix(self):
        assert self.traces_valid, 'Traces not generated yet'
        return self.filter_trace_matrix

    #
    def get_ofmap_sram_trace_matrix(self):
        assert self.traces_valid, 'Traces not generated yet'
        return self.ofmap_trace_matrix

    #
    def get_sram_trace_matrices(self):
        assert self.traces_valid, 'Traces not generated yet'
        return self.ifmap_trace_matrix, self.filter_trace_matrix, self.ofmap_trace_matrix

    #
    def get_ifmap_dram_trace_matrix(self):
        return self.ifmap_buf.get_trace_matrix()

    #
    def get_filter_dram_trace_matrix(self):
        return self.filter_buf.get_trace_matrix()

    #
    def get_ofmap_dram_trace_matrix(self):
        return self.ofmap_buf.get_trace_matrix()

    #
    def get_dram_trace_matrices(self):
        dram_ifmap_trace = self.ifmap_buf.get_trace_matrix()
        dram_filter_trace = self.filter_buf.get_trace_matrix()
        dram_ofmap_trace = self.ofmap_buf.get_trace_matrix()

        return dram_ifmap_trace, dram_filter_trace, dram_ofmap_trace

    #
    def print_ifmap_sram_trace(self, filename):
        assert self.traces_valid, 'Traces not generated yet'
        np.savetxt(filename, self.ifmap_trace_matrix, fmt='%i', delimiter=",")

    #
    def print_filter_sram_trace(self, filename):
        assert self.traces_valid, 'Traces not generated yet'
        np.savetxt(filename, self.filter_trace_matrix, fmt='%i', delimiter=",")

    #
    def print_ofmap_sram_trace(self, filename):
        assert self.traces_valid, 'Traces not generated yet'
        np.savetxt(filename, self.ofmap_trace_matrix, fmt='%i', delimiter=",")

    #
    def print_ifmap_dram_trace(self, filename):
        self.ifmap_buf.print_trace(filename)

    #
    def print_filter_dram_trace(self, filename):
        self.filter_buf.print_trace(filename)

    #
    def print_ofmap_dram_trace(self, filename):
        self.ofmap_buf.print_trace(filename)





