import subprocess
import re
import pandas as pd

# 定义正则表达式模式
duration_pattern = re.compile(r"Min: (\d+)ms\s+Max: (\d+)ms\s+Avg: (\d+)ms")
latency_pattern = re.compile(r"Avg latency \(us\)\]\s+(\d+)")
tps_qps_pattern = re.compile(r"Avg TPS/QPS\]\s+(\d+)\s+row per second")

# 读取CSV文件
file_path = 'HbasePeTest.csv'
df = pd.read_csv(file_path)
print(f"Read CSV file with {len(df)} rows.")

# 遍历每一行，执行命令并解析输出
for index, row in df.iterrows():
    command = row['Command']
    print(f"Executing command {index + 1}/{len(df)}: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output = stdout.decode('utf-8') + stderr.decode('utf-8')

    # 初始化结果
    min_duration, max_duration, avg_duration = None, None, None
    avg_latency, tps_qps = None, None

    # 解析输出结果
    duration_match = duration_pattern.search(output)
    if duration_match:
        min_duration = int(duration_match.group(1))
        max_duration = int(duration_match.group(2))
        avg_duration = int(duration_match.group(3))
        print(f"Parsed durations - Min: {min_duration}ms, Max: {max_duration}ms, Avg: {avg_duration}ms")

    latency_match = latency_pattern.search(output)
    if latency_match:
        avg_latency = int(latency_match.group(1))
        print(f"Parsed average latency: {avg_latency}us")

    tps_qps_match = tps_qps_pattern.search(output)
    if tps_qps_match:
        tps_qps = int(tps_qps_match.group(1))
        print(f"Parsed TPS/QPS: {tps_qps} rows/s")

    # 更新DataFrame
    df.at[index, 'Min Duration (ms)'] = min_duration
    df.at[index, 'Max Duration (ms)'] = max_duration
    df.at[index, 'Avg Duration (ms)'] = avg_duration
    df.at[index, 'Avg Latency (us)'] = avg_latency
    df.at[index, 'TPS/QPS (rows/s)'] = tps_qps
    print(f"Updated row {index + 1} in DataFrame.")

    # 保存更新后的CSV文件
    df.to_csv(file_path, index=False)
    print(f"Saved updated CSV after command {index + 1} execution.")

import ace_tools as tools; tools.display_dataframe_to_user(name="Updated HbasePeTest Results", dataframe=df)

