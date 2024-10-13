import pandas as pd

# 定义 TaskProfile 类
class TaskProfile:
    def __init__(self, task_id, task_name, channel_id, latency, blocking, blocked_channels, allowed_tasks_before_blocking):
        self.task_id = task_id
        self.task_name = task_name
        self.channel_id = channel_id
        self.latency = latency
        self.blocking = blocking
        self.start_cycle = 0
        self.end_cycle = 0
        self.stall_cycle = 0
        self.blocked_channels = blocked_channels
        self.allowed_tasks_before_blocking = allowed_tasks_before_blocking
    @staticmethod
    def simulate_pipeline(tasks):
        channel_end_cycles = {}
        channel_stall_times = {}
        results = []

        for task in tasks:
            channel_id = task.channel_id
            if channel_id in channel_end_cycles:
                start_cycle = channel_end_cycles[channel_id]
            else:
                start_cycle = 0

            for other_task in tasks:
                if task.channel_id in other_task.blocked_channels:
                    if other_task.end_cycle > start_cycle:
                        task.stall_cycle += other_task.end_cycle - start_cycle
                        start_cycle = other_task.end_cycle

            task.start_cycle = start_cycle
            task.end_cycle = task.start_cycle + task.latency
            channel_end_cycles[channel_id] = task.end_cycle

            if channel_id not in channel_stall_times:
                channel_stall_times[channel_id] = 0
            channel_stall_times[channel_id] += task.stall_cycle

            results.append({
                'task_id': task.task_id,
                'task_name': task.task_name,
                'channel_id': task.channel_id,
                'start_cycle': task.start_cycle,
                'end_cycle': task.end_cycle,
                'stall_cycle': task.stall_cycle,
                'blocked_channels': task.blocked_channels,
                'allowed_tasks_before_blocking': task.allowed_tasks_before_blocking
            })

        return results

# 定义解析日志并生成 TaskProfile 的函数
def parse_log_to_task_profiles(log_lines, default_channel_id=0):
    task_profiles = []
    task_counter = 1

    for line in log_lines:
        if "Funct" in line:
            parts = line.strip().split(',')
            funct_value = int(parts[0].split(':')[1].strip())  # 提取 Funct 值
            runtime_value = int(parts[2].split(':')[1].strip())  # 提取 Runtime 值

            if funct_value == 2: # mvin
                channel_id = 0 # LD
                blocking = True  
                blocked_channels = [1, 2]  
                tbb = 0
            elif funct_value == 3: # mvout
                channel_id = 1 # ST
                blocking = True  
                blocked_channels = [0, 2]  
                tbb = 0
            elif funct_value == 4: # comp_preload
                channel_id = 2 # EX
                blocking = True  
                blocked_channels = [0, 1]  
                tbb = 1
            elif funct_value == 5: # comp_accumulate
                channel_id = 2 # EX
                blocking = True  
                blocked_channels = [0, 1]  
                tbb = 1
            elif funct_value == 6: # preload
                channel_id = 2 # EX
                blocking = True  
                blocked_channels = [0, 1]  
                tbb = 1
            else:
                channel_id = default_channel_id
                blocking = False  # 默认不阻塞
                blocked_channels = []  # 默认没有阻塞其他通道
                tbb = 0

            # 创建 TaskProfile 实例
            task = TaskProfile( 
                task_id=task_counter, 
                task_name=f"Task {funct_value}", 
                channel_id=channel_id, 
                latency=runtime_value, 
                blocking=blocking, 
                blocked_channels=blocked_channels,
                allowed_tasks_before_blocking=tbb
            )

            task_profiles.append(task)
            task_counter += 1

    return task_profiles#pd.DataFrame(task_profiles)

# 读取日志文件并解析
log_file_path = './commit_stream/gemmini_funct_only.log'  # 替换为实际日志文件路径

with open(log_file_path, 'r') as file:
    log_content = file.readlines()

# 调用解析函数生成任务数据
task_profiles_df = parse_log_to_task_profiles(log_content)

# 显示生成的任务数据
print(task_profiles_df)
