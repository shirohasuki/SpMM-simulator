import sys
sys.path.append("../../../")

from spmmsim.utils.config.architecture import architecture as arch
from spmmsim.utils.config.workload import workload 
from single_layer_sim import single_layer_sim as layer_sim


class all_layers_sim:
    def __init__(self):
        self.arch = arch()
        self.workload = workload()

        self.output_path = "./"
        self.verbose = True
        self.save_trace = True

        self.num_layers = 0

        self.single_layer_sim_object_list = []

        self.params_set_flag = False
        self.all_layer_run_done = False
    
    def set_params(self, arch_obj=arch(), workload_obj=workload(),
                   output_path="./", verbosity=True, save_trace=True):

        self.arch = arch_obj
        self.workload = workload_obj

        self.output_path = output_path
        self.verbose = verbosity
        self.save_trace = save_trace

        # Calculate inferrable parameters here
        self.num_layers = self.workload.get_num_layers()

        self.params_set_flag = True