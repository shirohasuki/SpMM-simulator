# SpMM-simulator


### Run the source code
1. Set the PYTHONPATH environment variable. 

Make sure you are in the root directory.
```
$ export PYTHONPATH=$PWD:${PYTHONPATH}
```

### TODO
1. - [ ] TOOLs: 
   1. - [ ] 解析gemmini, 添加要供给Profile的latency
   2. - [ ] 解析gemmini, 确定task_profile需要的并行串行关系
2. - [ ] Model:
   1. - [ ] NVR: 添加NVR实现 
   2. - [ ] 添加scratchpad的模型，并能调节和cache(NPU内)比例
   3. - [ ] 添加新的计算模式
3. - [ ] Workload: 添加八个workload
