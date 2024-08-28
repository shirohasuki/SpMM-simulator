import configparser as cp


class architecture:
    # read architecture config information
    def __init__(self):
        self.run_name = "scale_run"
        # Anand: ISSUE #2. Patch
        self.use_user_bandwidth = False

        self.array_rows = 4
        self.array_cols = 4
        self.acache_sz_kb = 256
        self.bcache_sz_kb = 256
        self.ccache_sz_kb = 128
        self.dataflow = 'ws'
        self.acache_offset = 0
        self.bcache_offset = 10000000
        self.ccache_offset = 20000000
        self.workload = ""
        self.bandwidths = []
        self.valid_conf_flag = False

        self.valid_df_list = ['os', 'ws', 'is']

    # 读取arch文件信息
    def read_arch_file(self, arch_file_path):

        me = 'scale_arch.' + 'read_arch_file()'

        config = cp.ConfigParser()
        config.read(arch_file_path)

        # 读取general内容
        section = 'general'
        self.run_name = config.get(section, 'arch_name')

        # 读取run_presets内容
        section = 'presets'
        bw_mode_string = config.get(section, 'InterfaceBandwidth')
        if bw_mode_string == 'USER':
            self.use_user_bandwidth = True
        elif bw_mode_string == 'CALC':
            self.use_user_bandwidth = False
        else:
            message = 'ERROR: ' + me
            message += 'Use either USER or CALC in InterfaceBandwidth feild. Aborting!'
            return

        # 读取arch_presets内容
        section = 'architecture_presets'
        self.array_rows = int(config.get(section, 'ArrayHeight'))
        self.array_cols = int(config.get(section, 'ArrayWidth'))
        self.acache_sz_kb = int(config.get(section, 'AcacheSramszkB'))
        self.bcache_sz_kb = int(config.get(section, 'BcacheSramszkB'))
        self.ccache_sz_kb = int(config.get(section, 'CcacheSramszkB'))
        self.acache_offset = int(config.get(section, 'AcacheOffset'))
        self.bcache_offset = int(config.get(section, 'BcacheOffset'))
        self.ccache_offset = int(config.get(section, 'CcacheOffset'))
        self.dataflow = config.get(section, 'Dataflow')

        if self.use_user_bandwidth:
            self.bandwidths = [int(x.strip())
                               for x in config.get(section, 'Bandwidth').strip().split(',')]

        if self.dataflow not in self.valid_df_list:
            print("WARNING: Invalid dataflow")

        # 读取可选内容
        if config.has_section('network_presets'):  # Read network_presets
            self.workload = config.get(section, 'WorkloadCsvLoc').split('"')[1]

        self.valid_conf_flag = True

    #
    def set_workload_file(self, workload=''):
        self.workload = workload

    # #
    # def update_from_list(self, conf_list):
    #     if not len(conf_list) > 11:
    #         print("ERROR: scale_config.update_from_list: "
    #               "Incompatible number of elements in the list")

    #     self.run_name = conf_list[0]
    #     self.array_rows = int(conf_list[1])
    #     self.array_cols = int(conf_list[2])
    #     self.acache_sz_kb = int(conf_list[3])
    #     self.bcache_sz_kb = int(conf_list[4])
    #     self.ccache_sz_kb = int(conf_list[5])
    #     self.acache_offset = int(conf_list[6])
    #     self.bcache_offset = int(conf_list[7])
    #     self.ccache_offset = int(conf_list[8])
    #     self.df = conf_list[9]
    #     bw_mode_string = str(conf_list[10])

    #     assert bw_mode_string in ['CALC', 'USER'], 'Invalid mode of operation'
    #     if bw_mode_string == "USER":
    #         assert not len(conf_list) < 12, 'The user bandwidth needs to be provided'
    #         self.bandwidths = conf_list[11]
    #         self.use_user_bandwidth = True
    #     elif bw_mode_string == 'CALC':
    #         self.use_user_bandwidth = False

    #     if len(conf_list) == 15:
    #         self.topofile = conf_list[14]

    #     self.valid_conf_flag = True

    # #
    # def write_conf_file(self, conf_file_out):
    #     if not self.valid_conf_flag:
    #         print('ERROR: scale_config.write_conf_file: No valid config loaded')
    #         return

    #     config = cp.ConfigParser()

    #     section = 'general'
    #     config.add_section(section)
    #     config.set(section, 'run_name', str(self.run_name))

    #     section = 'architecture_presets'
    #     config.add_section(section)
    #     config.set(section, 'ArrayHeight', str(self.array_rows))
    #     config.set(section, 'ArrayWidth', str(self.array_cols))

    #     config.set(section, 'AcacheSramszkB', str(self.acache_sz_kb))
    #     config.set(section, 'BcacheSramszkB', str(self.bcache_sz_kb))
    #     config.set(section, 'CcacheSramszkB', str(self.ccache_sz_kb))

    #     config.set(section, 'AcacheOffset', str(self.acache_offset))
    #     config.set(section, 'BcacheOffset', str(self.bcache_offset))
    #     config.set(section, 'CcacheOffset', str(self.ccache_offset))

    #     config.set(section, 'Dataflow', str(self.df))
    #     config.set(section, 'Bandwidth', ','.join([str(x) for x in self.bandwidths]))

    #     section = 'network_presets'
    #     config.add_section(section)
    #     topofile = '"' + self.topofile + '"'
    #     config.set(section, 'TopologyCsvLoc', str(topofile))

    #     with open(conf_file_out, 'w') as configfile:
    #         config.write(configfile)

    # def set_arr_dims(self, rows=1, cols=1):
    #     self.array_rows = rows
    #     self.array_cols = cols

    # #
    # def set_dataflow(self, dataflow='os'):
    #     self.df = dataflow

    # #
    # def set_buffer_sizes_kb(self, acache_size_kb=1, bcache_size_kb=1, ccache_size_kb=1):
    #     self.acache_sz_kb = acache_size_kb
    #     self.bcache_sz_kb = bcache_size_kb
    #     self.ccache_sz_kb = ccache_size_kb



    # #
    # def set_offsets(self,
    #                 acache_offset=0,
    #                 bcache_offset=10000000,
    #                 ccache_offset=20000000
    #                 ):
    #     self.acache_offset = acache_offset
    #     self.bcache_offset = bcache_offset
    #     self.acache_offset = ccache_offset
    #     self.valid_conf_flag = True

    # #
    # def force_valid(self):
    #     self.valid_conf_flag = True

    # #
    # def set_bw_mode_to_calc(self):
    #     self.use_user_bandwidth = False

    # #
    # def use_user_dram_bandwidth(self):
    #     if not self.valid_conf_flag:
    #         me = 'scale_config.' + 'use_user_dram_bandwidth()'
    #         message = 'ERROR: ' + me + ': Configuration is not valid'
    #         print(message)
    #         return

    #     return self.use_user_bandwidth

    # #
    # def get_conf_as_list(self):
    #     out_list = []

    #     if not self.valid_conf_flag:
    #         print("ERROR: scale_config.get_conf_as_list: Configuration is not valid")
    #         return

    #     out_list.append(str(self.run_name))

    #     out_list.append(str(self.array_rows))
    #     out_list.append(str(self.array_cols))

    #     out_list.append(str(self.acache_sz_kb))
    #     out_list.append(str(self.bcache_sz_kb))
    #     out_list.append(str(self.ccache_sz_kb))

    #     out_list.append(str(self.acache_offset))
    #     out_list.append(str(self.bcache_offset))
    #     out_list.append(str(self.ccache_offset))

    #     out_list.append(str(self.df))
    #     out_list.append(str(self.topofile))
       
    #     return out_list
	
    # all_layers_sim use
    def get_run_name(self):
        if not self.valid_conf_flag:
            print("ERROR: scale_config.get_run_name() : Config data is not valid")
            return
        return self.run_name

    # def get_topology_path(self):
    #     if not self.valid_conf_flag:
    #         print("ERROR: scale_config.get_topology_path() : Config data is not valid")
    #         return
    #     return self.topofile

    # def get_topology_name(self):
    #     if not self.valid_conf_flag:
    #         print("ERROR: scale_config.get_topology_name() : Config data is not valid")
    #         return

    #     name = self.topofile.split('/')[-1].strip()
    #     name = name.split('.')[0]

    #     return name

    # def get_dataflow(self):
    #     if self.valid_conf_flag:
    #         return self.df

    # def get_array_dims(self):
    #     if self.valid_conf_flag:
    #         return self.array_rows, self.array_cols

    # def get_mem_sizes(self):
    #     me = 'scale_config.' + 'get_mem_sizes()'

    #     if not self.valid_conf_flag:
    #         message = 'ERROR: ' + me
    #         message += 'Config is not valid. Not returning any values'
    #         return

    #     return self.acache_sz_kb, self.bcache_sz_kb, self.ccache_sz_kb

    # def get_offsets(self):
    #     if self.valid_conf_flag:
    #         return self.acache_offset, self.bcache_offset, self.ccache_offset

    # def get_bandwidths_as_string(self):
    #     if self.valid_conf_flag:
    #         return ','.join([str(x) for x in self.bandwidths])

    # def get_bandwidths_as_list(self):
    #     if self.valid_conf_flag:
    #         return self.bandwidths

    # def get_min_dram_bandwidth(self):
    #     if not self.use_user_dram_bandwidth():
    #         me = 'scale_config.' + 'get_min_dram_bandwidth()'
    #         message = 'ERROR: ' + me + ': No user bandwidth provided'
    #         print(message)
    #     else:
    #         return min(self.bandwidths)

    # @staticmethod
    # def get_default_conf_as_list():
    #     dummy_obj = architecture()
    #     dummy_obj.force_valid()
    #     out_list = dummy_obj.get_conf_as_list()
    #     return out_list
