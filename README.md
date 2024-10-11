# SpMM-simulator

### Features
- Models we have
  - A cache simulator
  - A systolic_array model
  - A sparse compute model
- Tools we have
  - task profiler
  - custom inst decoder

### Run the source code
1. Set the PYTHONPATH environment variable. 

Make sure you are in the root directory.
```
$ export PYTHONPATH=$PWD:${PYTHONPATH}
```

### TODO
1. - [x] Tools: 
   1. - [x] 解析gemmini, 添加要供给Profile的latency
   2. - [x] 解析gemmini, 确定task_profile需要的并行串行关系
2. - [ ] Modeling:
   1. - [x] NVR: 添加NVR实现 
   2. - [x] 添加scratchpad的模型，并能调节和cache(NPU内)比例
   3. - [x] 添加新的计算模式
   4. - [ ] 添加对照DVR, IMP, stride prefetch
3. - [ ] Workload: 添加八个workload
