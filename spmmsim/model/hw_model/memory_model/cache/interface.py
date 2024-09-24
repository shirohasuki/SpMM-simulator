import argparse
import os
import configparser as cp

from cachesim import CacheSim

parser = argparse.ArgumentParser()
parser.add_argument('-c', metavar='Config file', type=str,
                        default="../scale.cfg",
                        help="Path to the config file")
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
miss_latency    = int(config.get(section, 'latency'))

sim = CacheSim()
sim.set_params(way, size, cacheline_size, replacement, 
               addr_size=32, data_size=data_size)
for i in range(0, 1000, 1):
    sim.cache_read(i, 0, 0, 0, True)
        # sim.sim.print_info()
sim.sim.print_info()

# 返回memory_access hit或者miss
def memory_access_eval(raddr, latency, 
                        way, size, cacheline_size, replacement, 
                        addr_size=32, data_size=data_size):
    if_hit = False
    latency = 0
    return if_hit, latency