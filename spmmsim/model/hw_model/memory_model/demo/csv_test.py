import pandas as pd
import numpy as np

import argparse
import os
import configparser as cp

import sys
sys.path.append("../")
from cachesim import CacheSim



if __name__ == '__main__':


    df = pd.read_csv('A_mem_access_pattern.csv', delimiter=',')

    # 去掉前两列
    df = df.iloc[:, 2:]
    # 替换所有NaN为-1
    df = df.fillna(-1)
    # 将DataFrame转换为NumPy矩阵
    # print(df.shape)

    matrix = df.to_numpy()[:,3:]
    
    matrix = np.array(matrix, dtype=int)
    # 输出结果
    # print(matrix.shape)


    parser = argparse.ArgumentParser()

    parser.add_argument('-c', metavar='Config file', type=str,
                        default="../scale.cfg",
                        help="Path to the config file"
                        )

    args   = parser.parse_args()
    
    config = args.c
    if not os.path.exists(config):
        print("ERROR: Config file not found") 
        print("Input file:" + config)
        print('Exiting')
        exit()
    else: 
        config_file = config

    config = cp.ConfigParser()
    config.read(config_file)

    section = 'cache_architecture_presets'
    size            = int(config.get(section, 'Total Size'))
    cacheline_size  = int(config.get(section, 'Cacheline Size'))
    way             = int(config.get(section, 'Way of Associativity'))
    replacement     = str(config.get(section, 'Way of Replacement'))
    data_size       = int(config.get(section, 'Data Size'))

    sim1 = CacheSim()
    sim2 = CacheSim()
    sim3 = CacheSim()
    sim1.set_params(way, size, cacheline_size, replacement, 32, data_size)
    sim2.set_params(way, size, cacheline_size, replacement, 32, data_size)
    sim3.set_params(way, size, cacheline_size, replacement, 32, data_size)
    # for i in range(0, 100, 1):
    #     sim.cache_read(i, 0, 0, 0, verbosity=True)
    import pdb
    

    
    print("int32: ")
    miss_times = 0
    miss_iters = 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if (matrix[i][j] != -1):
                # print(f"addr={matrix[j][i]}")
                sim1.cache_read(matrix[i][j]*4, 0, 0, 0, verbosity=False)
        if sim1.sim.miss > miss_times:
            miss_iters += 1
            miss_times = sim1.sim.miss
        # sim.sim.print_info()
            # pdb.set_trace()
    print(f"miss_times={miss_times}, miss_iters={miss_iters}")
    sim1.sim.print_info()

    print("FP16: ")
    miss_times = 0
    miss_iters = 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if (matrix[i][j] != -1):
                # print(f"addr={matrix[j][i]}")
                sim2.cache_read(matrix[i][j]*2, 0, 0, 0, verbosity=False)
        if sim2.sim.miss > miss_times:
            miss_iters += 1
            miss_times = sim2.sim.miss
    print(f"miss_times={miss_times}, miss_iters={miss_iters}")
    sim2.sim.print_info()

    print("int8: ")
    miss_times = 0
    miss_iters = 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if (matrix[i][j] != -1):
                # print(f"addr={matrix[j][i]}")
                sim2.cache_read(matrix[i][j]*1, 0, 0, 0, verbosity=False)
        if sim2.sim.miss > miss_times:
            miss_iters += 1
            miss_times = sim2.sim.miss
    print(f"miss_times={miss_times}, miss_iters={miss_iters}")
    sim2.sim.print_info()