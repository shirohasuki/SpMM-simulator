import pandas as pd
import matplotlib.pyplot as plt

class TaskProfile:
    def __init__(self, task_id, task_name, channel_id, latency, blocking, blocked_channels):
        self.task_id = task_id
        self.task_name = task_name  # 任务名称
        self.channel_id = channel_id  # 任务所属的channel
        self.blocking = blocking
        self.latency = latency
        self.start_cycle = 0
        self.end_cycle = 0
        self.stall_cycle = 0
        self.blocked_channels = blocked_channels  # 指定哪些channels会被block

    @staticmethod
    def simulate_pipeline(tasks):
        # 存储每个channel的当前结束时间和stall时间
        channel_end_cycles = {}
        channel_stall_times = {}

        results = []

        for task in tasks:
            # 获取当前channel的最早可开始时间
            channel_id = task.channel_id
            if channel_id in channel_end_cycles:
                start_cycle = channel_end_cycles[channel_id]
            else:
                start_cycle = 0

            # 检查是否有其他任务阻塞了该任务所在的channel
            for other_task in tasks:
                if task.channel_id in other_task.blocked_channels:
                    if other_task.end_cycle > start_cycle:
                        task.stall_cycle += other_task.end_cycle - start_cycle
                        start_cycle = other_task.end_cycle

            # 如果当前任务是阻塞任务，更新它阻塞的channel的结束时间
            if task.blocking:
                for blocked_channel in task.blocked_channels:
                    if blocked_channel in channel_end_cycles:
                        if channel_end_cycles[blocked_channel] < task.end_cycle:
                            channel_end_cycles[blocked_channel] = task.end_cycle

            # 计算任务的开始时间和结束时间
            task.start_cycle = start_cycle
            task.end_cycle = task.start_cycle + task.latency

            # 更新该channel的结束时间
            channel_end_cycles[channel_id] = task.end_cycle

            # 累加该channel的stall时间
            if channel_id not in channel_stall_times:
                channel_stall_times[channel_id] = 0
            channel_stall_times[channel_id] += task.stall_cycle
            # print(f"channel_id {channel_id} task.stall_cycle {task.stall_cycle} {channel_stall_times[channel_id]}")

            # 将任务信息记录下来
            results.append({
                'task_id': task.task_id,
                'task_name': task.task_name,  # 记录task_name
                'channel_id': task.channel_id,  # 记录channel_id
                'start_cycle': task.start_cycle,
                'end_cycle': task.end_cycle,
                'stall_cycle': task.stall_cycle,
                'blocked_channels': task.blocked_channels  # 被阻塞的channels
            })

        # 找出最后完成的channel
        final_channel = max(channel_end_cycles, key=channel_end_cycles.get)
        final_end_cycle = channel_end_cycles[final_channel]
        final_stall_time = channel_stall_times[final_channel]

        print(f"Key Path: Channel {final_channel}")
        print(f"Total Time: {final_end_cycle} cycles")
        print(f"Total Stall Time: {final_stall_time} cycles")

        return results

    @staticmethod
    def visualize_pipeline(tasks):
        # 按channel_id进行分组和排序
        tasks_sorted = sorted(tasks, key=lambda x: x.channel_id)

        fig, ax = plt.subplots(figsize=(10, 2))

        # 设置xy轴的范围
        ax.set_ylim(-1, 2)
        ax.set_xlim(0, 100)

        # 记录绘制的Y轴对应的channel
        channel_positions = {}
        current_channel_position = 0

        for task in tasks_sorted:
            # 如果是新的channel，更新绘图的位置
            if task.channel_id not in channel_positions:
                channel_positions[task.channel_id] = current_channel_position
                current_channel_position += 1

            # 任务的起始时间和长度
            start_cycle = task.start_cycle
            duration = task.latency
            channel_y_position = channel_positions[task.channel_id]

            # 可视化任务的执行区间，设置边框颜色和宽度
            ax.barh(channel_y_position, duration, 
                    left=start_cycle, color='green', edgecolor='black', linewidth=1)

            # 在条形图中间添加任务名称
            ax.text(start_cycle + duration / 2, channel_y_position, task.task_name, 
                    va='center', ha='center', color='white', fontweight='bold')

            # 如果存在等待时间，绘制等待时间的部分，设置边框颜色和宽度
            if task.stall_cycle > 0:
                ax.barh(channel_y_position, task.stall_cycle, 
                        left=start_cycle - task.stall_cycle, color='red', edgecolor='black', linewidth=1)

                # 在等待的红色部分添加文本
                ax.text(start_cycle - task.stall_cycle / 2, channel_y_position, 'Stalling',
                        va='center', ha='center', color='white', fontweight='bold')

        # 设置Y轴标签为对应的channel
        ax.set_yticks(list(channel_positions.values()))
        ax.set_yticklabels([f'Channel {channel_id}' for channel_id in channel_positions.keys()])

        ax.set_xlabel('cycle')
        ax.set_ylabel('Channels')
        ax.set_title('Task Execution Timeline')

        plt.show()

if __name__ == "__main__":
    tasks = [
        TaskProfile(1, "Task A", channel_id=0, latency=10, blocking=True, blocked_channels=[1]),
        TaskProfile(2, "Task B", channel_id=0, latency=15, blocking=False, blocked_channels=[]),
        TaskProfile(3, "Task C", channel_id=1, latency=12, blocking=False, blocked_channels=[]),
        TaskProfile(4, "Task D", channel_id=1, latency=15, blocking=True, blocked_channels=[0]),
        TaskProfile(5, "Task E", channel_id=0, latency=20, blocking=True, blocked_channels=[1]),
        TaskProfile(6, "Task F", channel_id=1, latency=15, blocking=False, blocked_channels=[]),
        TaskProfile(7, "Task G", channel_id=0, latency=20, blocking=False, blocked_channels=[]),
        TaskProfile(8, "Task H", channel_id=0, latency=10, blocking=False, blocked_channels=[])
    ]

    results = TaskProfile.simulate_pipeline(tasks)
    df = pd.DataFrame(results)
    print(df)

    # 可视化任务的执行流水线
    TaskProfile.visualize_pipeline(tasks)
