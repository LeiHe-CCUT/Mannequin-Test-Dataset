import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 设置 Seaborn 配色方案
sns.set_palette("Set2")  # 选择一个色彩和谐的配色方案

# 定义绘图函数
def plot_data(data, time_col, value_cols, labels, colors, markers, title, xlabel, ylabel):
    plt.figure(figsize=(12, 8))  # 定义图形大小
    for i, col in enumerate(value_cols):
        plt.plot(data[time_col], data[col], label=labels[i], color=colors[i], linestyle='-', marker=markers[i], markersize=6, alpha=0.8)
    
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.title(title, fontsize=16)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)  # 使用虚线网格并设置透明度
    plt.tight_layout()  # 自动调整布局，避免标签重叠
    plt.show()

# 读取数据并转换时间
def read_and_prepare_data(file_path, time_col):
    data = pd.read_csv(file_path)
    data['TimeSec'] = data[time_col] / 1000  # 将时间从毫秒转换为秒
    return data

# 图1：位置 vs 时间（经度与纬度）
data1 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols8_9.csv", 'TimeMs')
plot_data(data1, 'TimeSec', ['PosLon', 'PosLat'], ['Longitude (PosLon)', 'Latitude (PosLat)'], 
          ['b', 'g'], ['o', 'x'], 'Position vs Time (Longitude and Latitude)', 'Time (seconds)', 'Position')

# 图2：海拔 vs 时间
data2 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols10.csv", 'TimeMs')
plot_data(data2, 'TimeSec', ['Altitude'], ['Altitude'], 
          ['r'], ['^'], 'Altitude vs Time', 'Time (seconds)', 'Altitude')

# 图3：2D速度 vs 时间
data3 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols11.csv", 'TimeMs')
plot_data(data3, 'TimeSec', ['Speed2D'], ['Speed2D'], 
          ['c'], ['s'], 'Speed2D vs Time', 'Time (seconds)', 'Speed2D')

# 图4：角加速度 vs 时间
data4 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols12_13_14.csv", 'TimeMs')
plot_data(data4, 'TimeSec', ['AngAccelX', 'AngAccelY', 'AngAccelZ'], ['AngAccelX', 'AngAccelY', 'AngAccelZ'], 
          ['b', 'g', 'r'], ['o', '^', 's'], 'AngAccelX AngAccelY AngAccelZ vs Time', 'Time (seconds)', 'AngAccel')

# 图5：前进与侧向速度 vs 时间
data5 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols15_16.csv", 'TimeMs')
plot_data(data5, 'TimeSec', ['VelForward', 'VelLateral'], ['VelForward', 'VelLateral'], 
          ['b', 'g'], ['o', 'x'], 'VelForward VelLateral vs Time', 'Time (seconds)', 'Velocity')

# 图6：加速度 vs 时间
data6 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols17_18_19.csv", 'TimeMs')
plot_data(data6, 'TimeSec', ['AccelX', 'AccelY', 'AccelZ'], ['AccelX', 'AccelY', 'AccelZ'], 
          ['b', 'g', 'r'], ['o', '^', 's'], 'AccelX AccelY AccelZ vs Time', 'Time (seconds)', 'Acceleration')

# 图7：前进、侧向与滑移加速度 vs 时间
data7 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols20_21_22.csv", 'TimeMs')
plot_data(data7, 'TimeSec', ['AccelForward', 'AccelLateral', 'AccelSlip'], ['AccelForward', 'AccelLateral', 'AccelSlip'], 
          ['b', 'g', 'r'], ['o', 'x', '^'], 'AccelForward AccelLateral AccelSlip vs Time', 'Time (seconds)', 'Acceleration')

# 图8：姿态角度 vs 时间
data8 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols23_24_25.csv", 'TimeMs')
plot_data(data8, 'TimeSec', ['AngleHeading', 'AnglePitch', 'AngleRoll'], ['AngleHeading', 'AnglePitch', 'AngleRoll'], 
          ['b', 'g', 'r'], ['o', 'x', '^'], 'AngleHeading AnglePitch AngleRoll vs Time', 'Time (seconds)', 'Angle')

# 图9：角速率 vs 时间
data9 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols26_27_28.csv", 'TimeMs')
plot_data(data9, 'TimeSec', ['AngRateX', 'AngRateY', 'AngRateZ'], ['AngRateX', 'AngRateY', 'AngRateZ'], 
          ['b', 'g', 'r'], ['o', 's', '^'], 'AngRateX AngRateY AngRateZ vs Time', 'Time (seconds)', 'AngRate')

# 图10：前进与侧向角速率 vs 时间
data10 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols29_30.csv", 'TimeMs')
plot_data(data10, 'TimeSec', ['AngRateForward', 'AngRateLateral'], ['AngRateForward', 'AngRateLateral'], 
          ['b', 'g'], ['o', 'x'], 'AngRateForward AngRateLateral vs Time', 'Time (seconds)', 'AngRate')

# 图11：距离与保持距离 vs 时间
data11 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols31_32.csv", 'TimeMs')
plot_data(data11, 'TimeSec', ['DistanceWithHold', 'Distance'], ['DistanceWithHold', 'Distance'], 
          ['b', 'g'], ['o', 'x'], 'DistanceWithHold Distance vs Time', 'Time (seconds)', 'Distance')

# 图12：本地坐标 vs 时间
data12 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols33_34.csv", 'TimeMs')
plot_data(data12, 'TimeSec', ['PosLocalX', 'PosLocalY'], ['PosLocalX', 'PosLocalY'], 
          ['b', 'g'], ['o', 'x'], 'PosLocalX PosLocalY vs Time', 'Time (seconds)', 'Position')

# 图13：速度与角度 vs 时间
data13 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols35_36_37_38.csv", 'TimeMs')
plot_data(data13, 'TimeSec', ['VelLocalX', 'VelLocalY', 'AngleLocalYaw', 'AngleLocalTrack'], ['VelLocalX', 'VelLocalY', 'AngleLocalYaw', 'AngleLocalTrack'], 
          ['b', 'g', 'r', 'm'], ['o', 'x', '^', 's'], 'Velocities and Angles vs Time', 'Time (seconds)', 'Value')

# 图14：前进与侧向加速度 vs 时间
data14 = read_and_prepare_data(r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\cols39_40.csv", 'TimeMs')
plot_data(data14, 'TimeSec', ['AngAccelForward', 'AngAccelLateral'], ['AngAccelForward', 'AngAccelLateral'], 
          ['b', 'g'], ['o', 'x'], 'AngAccelForward AngAccelLateral vs Time', 'Time (seconds)', 'AngAccel')
