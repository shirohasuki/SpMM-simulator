import argparse
import os
import configparser as cp

import sys
sys.path.append("../")
from cachesim import CacheSim

if __name__ == '__main__':
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

    sim = CacheSim()
    sim.set_params(way, size, cacheline_size, replacement, 32, data_size)
    for i in range(0, 1000, 1):
        sim.cache_read(i, 0, 0, 0, True)
        # sim.sim.print_info()

    sim.sim.print_info()
