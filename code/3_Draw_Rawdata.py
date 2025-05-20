import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 设置 Seaborn 配色方案
sns.set_palette("Set2")

# 定义绘图函数
def plot_data(data, time_col, value_cols, labels, colors, markers, ylabel, save_path):
    plt.figure(figsize=(14, 6))  # 更长比例
    for i, col in enumerate(value_cols):
        plt.plot(
            data[time_col], data[col],
            label=labels[i],
            color=colors[i],
            linestyle='-',
            marker=markers[i],
            markersize=6,
            alpha=0.8,
            linewidth=2  # 加粗线条
        )
    plt.xlabel("Time (seconds)", fontsize=14, fontweight='bold')
    plt.ylabel(ylabel, fontsize=14, fontweight='bold')
    plt.tick_params(axis='both', which='major', labelsize=12)

    # ✅ 加粗坐标轴数字
    ax = plt.gca()
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12, loc='best', frameon=True, fancybox=True)
    for text in ax.get_legend().get_texts():
        text.set_fontweight('bold')  # 加粗图例文字
    plt.tight_layout()
    plt.savefig(save_path, dpi=400)
    plt.close()



# 读取数据并清理列名
def read_and_prepare_data(file_path, time_col='TimeMs'):
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()  # 清除列名空格
    if time_col not in data.columns:
        raise ValueError(f"⛔ '{time_col}' not found in {file_path}")
    data['TimeSec'] = data[time_col] / 1000
    return data


# 数据所在目录
# base_dir = r"E:\何磊\子刊讨论\Mannequin Test Dataset\06-10-2013-NoVideo\Original Recorded Data\Data"
# base_dir = r"E:\何磊\子刊讨论\Mannequin Test Dataset\06-10-2013-NoVideo\Original Recorded Data\Data\30km_running_hit"
# base_dir = r"E:\何磊\子刊讨论\Mannequin Test Dataset\06-10-2013-NoVideo\Original Recorded Data\Data\30km_walking_success"
# base_dir = r"E:\何磊\子刊讨论\Mannequin Test Dataset\06-10-2013-NoVideo\Original Recorded Data\Data\30km_running_success"
base_dir = r"E:\何磊\子刊讨论\Mannequin Test Dataset\06-10-2013-NoVideo\Original Recorded Data\Data\30_static"

output_dir = os.path.join(base_dir, "output_figs")
os.makedirs(output_dir, exist_ok=True)

# 配置每个图的文件名和绘图参数
plot_configs = [
    ("cols8_9.csv", ['PosLon', 'PosLat'], ['Longitude (PosLon)', 'Latitude (PosLat)'], ['b', 'g'], ['o', 'x'], 'Position'),
    ("cols10.csv", ['Altitude'], ['Altitude'], ['r'], ['^'], 'Altitude'),
    ("cols11.csv", ['Speed2D'], ['Speed2D'], ['c'], ['s'], 'Speed2D'),
    ("cols12_13_14.csv", ['AngAccelX', 'AngAccelY', 'AngAccelZ'], ['AngAccelX', 'AngAccelY', 'AngAccelZ'], ['b', 'g', 'r'], ['o', '^', 's'], 'AngAccel'),
    ("cols15_16.csv", ['VelForward', 'VelLateral'], ['VelForward', 'VelLateral'], ['b', 'g'], ['o', 'x'], 'Velocity'),
    ("cols17_18_19.csv", ['AccelX', 'AccelY', 'AccelZ'], ['AccelX', 'AccelY', 'AccelZ'], ['b', 'g', 'r'], ['o', '^', 's'], 'Acceleration'),
    ("cols20_21_22.csv", ['AccelForward', 'AccelLateral', 'AccelSlip'], ['AccelForward', 'AccelLateral', 'AccelSlip'], ['b', 'g', 'r'], ['o', 'x', '^'], 'Acceleration'),
    ("cols23_24_25.csv", ['AngleHeading', 'AnglePitch', 'AngleRoll'], ['AngleHeading', 'AnglePitch', 'AngleRoll'], ['b', 'g', 'r'], ['o', 'x', '^'], 'Angle'),
    ("cols26_27_28.csv", ['AngRateX', 'AngRateY', 'AngRateZ'], ['AngRateX', 'AngRateY', 'AngRateZ'], ['b', 'g', 'r'], ['o', 's', '^'], 'AngRate'),
    ("cols29_30.csv", ['AngRateForward', 'AngRateLateral'], ['AngRateForward', 'AngRateLateral'], ['b', 'g'], ['o', 'x'], 'AngRate'),
    ("cols31_32.csv", ['DistanceWithHold', 'Distance'], ['DistanceWithHold', 'Distance'], ['b', 'g'], ['o', 'x'], 'Distance'),
    ("cols33_34.csv", ['PosLocalX', 'PosLocalY'], ['PosLocalX', 'PosLocalY'], ['b', 'g'], ['o', 'x'], 'Position'),
    ("cols35_36_37_38.csv", ['VelLocalX', 'VelLocalY', 'AngleLocalYaw', 'AngleLocalTrack'], ['VelLocalX', 'VelLocalY', 'AngleLocalYaw', 'AngleLocalTrack'], ['b', 'g', 'r', 'm'], ['o', 'x', '^', 's'], 'Value'),
    ("cols39_40.csv", ['AngAccelForward', 'AngAccelLateral'], ['AngAccelForward', 'AngAccelLateral'], ['b', 'g'], ['o', 'x'], 'AngAccel'),
]

# 批量绘图
for filename, cols, labels, colors, markers, ylabel in plot_configs:
    file_path = os.path.join(base_dir, filename)
    try:
        data = read_and_prepare_data(file_path)
    except Exception as e:
        print(f"⚠️ 跳过 {filename}: {e}")
        continue

    # 检查缺失列
    missing_cols = [col for col in cols if col not in data.columns]
    if missing_cols:
        print(f"⛔ 缺失列 in {filename}: {missing_cols}")
        continue

    save_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.png")
    plot_data(data, 'TimeSec', cols, labels, colors, markers, ylabel, save_path)

print("✅ 所有图像绘制并保存完成。输出路径：", output_dir)
