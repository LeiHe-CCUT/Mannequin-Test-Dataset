import os
import numpy as np
import pandas as pd
import scipy.io
import matplotlib.pyplot as plt

# 设置工作目录和读取Excel文件
date = '06-25-2014'
excel_data = pd.read_excel('Datasheet7-22.xlsx', header=None)
raw = excel_data.values

# 创建保存图像的文件夹
os.makedirs(f'{date}/Pics2', exist_ok=True)

# 读取数据文件目录
data_dir = f'{date}/Processed Data/Diag_{date}/Data'
mat_files = [f for f in os.listdir(data_dir) if f.endswith('.mat')]

mat_files = mat_files[2:]  # 跳过前两个文件（对应 MATLAB 中的从索引 3 开始）

for filename in mat_files:
    filepath = os.path.join(data_dir, filename)
    mat_data = scipy.io.loadmat(filepath, struct_as_record=False, squeeze_me=True)

    Data = mat_data['Data']
    line_num = int(filename[:3])

    speed = Data.Speed.Value
    time_speed = Data.Speed.Time
    acc = -np.diff(speed) / np.diff(time_speed)
    max_value = np.max(acc)
    max_id = np.argmax(acc)

    try:
        vehicle_stop = np.where(speed == 0)[0][0]
    except IndexError:
        vehicle_stop = 999999

    try:
        vehicle_pass = np.where(Data.LocalPosX.Value < 0)[0][0]
    except IndexError:
        vehicle_pass = len(Data.LocalPosX.Value)

    end_point = min(vehicle_stop, vehicle_pass)

    if not hasattr(Data, 'RealTimePosHour'):
        if hasattr(Data, 'DashLightHour'):
            t = len(Data.Hour.Value)
            b = len(Data.LocalPosX.Value)

            for c in range(b):
                if Data.LocalPosX.Value[c] < 10:
                    break

            time_rt = time_speed
            dash_time = (Data.DashLightHour.Value * 3600 + 
                         Data.DashLightMinute.Value * 60 + 
                         Data.DashLightMilliseconds.Value / 1000)

            least = Data.LocalPosX.Value[0]
            least_index = 0
            for i in range(1, b):
                if abs(Data.LocalPosX.Value[i]) < least:
                    least = abs(Data.LocalPosX.Value[i])
                    least_index = i

            collision_dash_time = 0
            for i2, dt in enumerate(dash_time):
                if time_rt[max_id] - dt < 3:
                    collision_dash_time = dt
                    td = time_rt[max_id] - dt
                    break

            warning_duration = dash_time[-1] - dash_time[i2]

            dash_light_index = 0
            dash_least = abs(Data.LocalPosX.Time[0] - collision_dash_time)
            for i in range(b):
                diff = abs(Data.LocalPosX.Time[i] - collision_dash_time)
                if diff < dash_least:
                    dash_least = diff
                    dash_light_index = i

            dash_light_index = max(dash_light_index, 501)

            ind = np.where(Data.LocalPosX.Value <= 10)[0][0]
            average_speed = Data.Speed.Value[ind] * 2.23694
            v_near = average_speed
            v_mod = v_near % 5
            v_desire = v_near - v_mod + 5 if v_mod > 2.5 else v_near - v_mod

            if hasattr(Data, 'BrakeLightHour'):
                brake_time = (Data.BrakeLightHour.Value * 3600 + 
                              Data.BrakeLightMinute.Value * 60 + 
                              Data.BrakeLightMilliseconds.Value / 1000)

                auto_brake_time = 0
                warning_to_braking = 0
                for bt in brake_time:
                    if abs(bt - collision_dash_time) < 2:
                        warning_to_braking = bt - collision_dash_time
                        auto_brake_time = bt
                        break

                brake_index = 0
                brake_least = abs(Data.LocalPosX.Time[0] - auto_brake_time)
                for i in range(b):
                    diff = abs(Data.LocalPosX.Time[i] - auto_brake_time)
                    if diff < brake_least:
                        brake_least = diff
                        brake_index = i
            else:
                warning_to_braking = 'N/A'
                brake_index = 0

            warning_distance = Data.LocalPosX.Value[dash_light_index]
            A = Data.Speed.Value[least_index] * 2.23694
            if A < 0.16:
                A = 0

            warning_to_collision = time_rt[least_index] - dash_time[0]
            distance_to_collision = least

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(Data.LocalPosX.Time, Data.LocalPosX.Value, linewidth=2, label='Distance (m)')
            full_time = (Data.Hour.Value * 3600 + Data.Minute.Value * 60 +
                         Data.Second.Value + Data.HundredthsSecond.Value)
            ax.plot(full_time[:t - 1], Data.Speed.Value[:t - 1] * 2.23694, 'k-', linewidth=2, label='Vehicle Speed (mph)')

            ax.set_ylim([-20, 60])
            ax.set_xlim([time_rt[c] - 10, time_rt[c] + 10])
            ax.set_xlabel('Time(s)', fontsize=20)
            ax.set_yticks(np.arange(-20, 65, 5))
            ax.set_xticks(np.arange(time_rt[c] - 10, time_rt[c] + 11, 2))
            ax.grid(True)
            ax.legend(fontsize=12)

            if hasattr(Data, 'BrakeLightHour'):
                brake_x = (Data.BrakeLightHour.Value * 3600 +
                           Data.BrakeLightMinute.Value * 60 +
                           Data.BrakeLightMilliseconds.Value / 1000)
                ax.plot(brake_x, Data.BrakeLight.Value + 30, '^:', color='orange', label='BrakeLight')

            dash_x = dash_time
            ax.plot(dash_x, Data.DashLight.Value + 40, '*:', color='red', label='DashLight')

            if Data.LocalPosX.Value[end_point] <= 0:
                ax.axvline(x=time_rt[least_index], color='blue', label='Collision point')

plt.close('all')  # 结束时关闭所有图像窗口以释放资源
