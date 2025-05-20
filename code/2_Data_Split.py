import pandas as pd
import os

def split_csv_combinations(input_file, output_dir):
    """
    读取 CSV 文件后，将前 7 列与以下各组的列组合输出成单独的 CSV 文件：
      (8,9), (10), (11), (12,13,14), (15,16), (17,18,19), (20,21,22),
      (23,24,25), (26,27,28), (29,30), (31,32), (33,34), (35,36),
      (37,38,39), (40,41,42)
    如果某个组合中的列超出了 CSV 文件实际列数，则跳过该组合。
    """
    # 1. 读取原始 CSV 文件，全部以字符串方式读入
    df = pd.read_csv(input_file, dtype=str, encoding='utf-8')
    total_cols = df.shape[1]  # CSV 文件的总列数
    print(f"CSV 文件总列数：{total_cols}")

    # 2. 定义需要组合的列组（人类可见列号，从1开始计数）
    groups = [
        [8, 9],
        [10],
        [11],
        [12, 13, 14],
        [15, 16],
        [17, 18, 19],
        [20, 21, 22],
        [23, 24, 25],
        [26, 27, 28],
        [29, 30],
        [31, 32],
        [33, 34],
        [35, 36,37, 38],
        [39,40],
    ]
    
     # 3. 前7列的人类可见列号：1~7，对应 pandas 索引 0~6
    front7_indices = list(range(0, 7))
    
    # 4. 对每个组合进行处理与输出 CSV 文件
    for group in groups:
        # 将人类可见列号转换为 pandas 的零基索引
        group_indices = [c - 1 for c in group]
        all_indices = front7_indices + group_indices
        
        # 检查所需的最大索引是否超过 CSV 文件的列数
        if max(all_indices) >= total_cols:
            print(f"警告：组合 {group} 对应的索引 {max(all_indices)+1} 超出 CSV 文件列数，跳过该组合。")
            continue
        
        # 复制子 DataFrame
        sub_df = df.iloc[:, all_indices].copy()
        
        # 将组合列（即前7列之后的部分）的空字符串替换为 NA
        sub_df.iloc[:, 7:] = sub_df.iloc[:, 7:].replace(r'^\s*$', pd.NA, regex=True)
        
        # 删除组合列中所有单元格均为空的行
        sub_df = sub_df[sub_df.iloc[:, 7:].notna().any(axis=1)]
        
        # 可选：重置行索引
        sub_df.reset_index(drop=True, inplace=True)
        
        # 根据组合列构造输出文件名，如 cols8_9.csv、cols10.csv、cols12_13_14.csv 等
        group_str = "_".join(str(c) for c in group)
        out_filename = f"cols{group_str}.csv"
        out_path = os.path.join(output_dir, out_filename)
        
        sub_df.to_csv(out_path, index=False, encoding='utf-8-sig')
        print(f"已输出: {out_path}")

if __name__ == "__main__":
    # 修改为你自己的输入 CSV 文件路径
    input_file = r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data\4A-30-15-A-1-H.csv"
    # 修改为你想要保存的输出文件夹路径
    output_dir = r"C:\Users\17845\Desktop\子刊讨论\PCS Test Data\bicyclist\06-28-2016\DGPS and carrier data"
    
    # 如果输出文件夹不存在，则创建
    os.makedirs(output_dir, exist_ok=True)
    
    split_csv_combinations(input_file, output_dir)
