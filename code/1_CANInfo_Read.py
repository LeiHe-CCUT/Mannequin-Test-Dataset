import struct
import csv
import os

class CANMessageInfo:
    def __init__(self, lineString, timeMs=None):
        """
        解析一行文本，构造 CANMessageInfo 对象。  
        原始 C# 代码逻辑：  
          - tokens[0]：消息编号（去掉末尾的符号，例如 "2)" 变成 "2"）  
          - tokens[1]：时间偏移  
          - tokens[4]：消息 ID（16进制）  
          - tokens[6]：数据长度  
          - tokens[7..]：payload（16进制，每个 token 表示一个字节）  
        """
        tokens = lineString.split()
        # 去掉 tokens[0] 末尾的右括号（如 "2)" -> "2"）
        message_number_str = tokens[0].rstrip(')')
        self.messageNumber = int(message_number_str)
        self.timeOffset = float(tokens[1])
        # tokens[2] 和 tokens[3]（总线号、方向）不作处理
        self.messageId = int(tokens[4], 16)
        self.length = int(tokens[6])
        # 解析 payload：从 tokens[7] 开始取 length 个字节
        payload_tokens = tokens[7:7+self.length]
        self.payload = bytearray(int(tok, 16) for tok in payload_tokens)
        
        # 默认 timeMs 等于 timeOffset，如果传入了 timeMs 则使用传入值
        if timeMs is None:
            self._timeMs = self.timeOffset
        else:
            self._timeMs = timeMs

        self._update_timeString()

 #       self.GetFloats()

    def _update_timeString(self):
        """
        根据 _timeMs 计算时间字符串（格式：hour:minute:second:ms）  
        注意：这里为了与 C# 保持一致，用整数截断毫秒。
        """
        total = int(self._timeMs)
        hour = total // 3600000
        rem = total % 3600000
        minute = rem // 60000
        rem = rem % 60000
        second = rem // 1000
        ms = rem % 1000
        self.timeString = f"{hour}:{minute}:{second}:{ms}"

    @property
    def timeMs(self):
        return self._timeMs

    @timeMs.setter
    def timeMs(self, value):
        self._timeMs = value
        self._update_timeString()

    def GetTimeMs(self):
        """
        根据 payload 中第 5～8 个字节计算时间（毫秒），公式为：  
          payload[7] * 3600000 + payload[6] * 60000 + payload[5] * 1000 + payload[4] * 10  
        若 payload 长度不足 8 字节，则返回 0。
        """
        if len(self.payload) >= 8:
            return (self.payload[7] * 3600000 +
                    self.payload[6] * 60000 +
                    self.payload[5] * 1000 +
                    self.payload[4] * 10)
        return 0

    def GetFloats(self, offset, factor, fmt):
        """
        根据 fmt 解析 payload 中的数据，并乘以因子 factor。  
          - fmt == 1: 按无符号 2 字节解析  
          - fmt == 2: 按有符号 16 位解析  
          - fmt == 4: 按有符号 32 位解析  
          - fmt == 8: 按有符号 64 位解析  
          - 未提供 fmt，则默认按 Int16 解析。
        """

        if fmt is None:
            return self._get_int16(offset) * factor
        else:
            if fmt == 1:
                return self._get_char(offset) * factor
            elif fmt == 2:
                return self._get_int16(offset) * factor
            elif fmt == 4:
                return self._get_int32(offset) * factor
            elif fmt == 8:
                return self._get_int64(offset) * factor
            else:
                return self._get_int16(offset) * factor

    def _get_char(self, offset):
        return struct.unpack_from('<H', self.payload, offset)[0]

    # def _get_int16(self, offset):
    #     return struct.unpack_from('<h', self.payload, offset)[0]
    def _get_int16(self, offset):
        if len(self.payload) < offset + 2:
            # 根据实际需求处理数据不足的情况，比如返回默认值或者跳过该字段
            return 0  # 这里返回0作为默认值
        return struct.unpack_from('<h', self.payload, offset)[0]
    def _get_int32(self, offset):
        return struct.unpack_from('<i', self.payload, offset)[0]

    def _get_int64(self, offset):
        return struct.unpack_from('<q', self.payload, offset)[0]

    def _get_int16(self, offset):
        if len(self.payload) < offset + 2:
            # 根据实际需求处理数据不足的情况，比如返回默认值或者跳过该字段
            return 0  # 这里返回0作为默认值
        return struct.unpack_from('<h', self.payload, offset)[0]

class CANMessage:
    def __init__(self, fileName):
        """
        解析 .trc 文件中的 CAN 消息，并生成 CSV 文件。  
        逻辑说明（参考 C# 代码）：  
          - 跳过前 21 行（及空行或注释行）  
          - 仅解析长度大于 40 的行  
          - 如果遇到 messageId==0x600 的消息，则用 GetTimeMs() 得到绝对时间，
            同时调整之前所有消息的时间戳  
          - 其它消息的时间戳根据上一个 0x600 消息的时间偏移累加计算
          - 解析结果写入与源文件同名但扩展名为 .csv 的文件中
        """
        self.messageList = []
        lastTimeMessage = None
        ifTimeMessage = False
        PosLat = None
        PosLon = None
        AccelX = None
        AccelY = None
        AccelZ =None
        AngRateX =None
        AngRateY=None
        AngRateZ=None
        Altitude = None
        AngAccelX = None
        AngAccelY = None
        AngAccelZ = None
        VelForward = None
        VelLateral= None
        Speed2D = None
        AccelForward  = None
        AccelLateral  = None
        AccelSlip = None
        AngleHeading = None
        AnglePitch = None
        AngleRoll = None
        AngRateForward = None
        AngRateLateral = None
        DistanceWithHold = None
        Distance = None
        AngAccelForward = None
        AngAccelLateral = None
        VelLocalX = None
        VelLocalY= None
        AngleLocalYaw = None
        AngleLocalTrack= None


        # 生成同级目录下同名 .csv 文件名
        base, _ = os.path.splitext(fileName)
        csv_filename = base + ".csv"

        with open(fileName, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()

        with open(csv_filename, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.writer(f_out)
            # 写入 CSV 表头
            writer.writerow([
                "MessageNumber",
                "TimeOffset",
                "MessageID(hex)",
                "Length",
                "Payload(hex)",
                "TimeMs",
                "TimeString",
                "PosLon","PosLat",
                "Altitude",
                "Speed2D",
                "AngAccelX","AngAccelY","AngAccelZ",
                "VelForward","VelLateral",
                "AccelX","AccelY","AccelZ",
                "AccelForward", "AccelLateral","AccelSlip", 
                "AngleHeading","AnglePitch","AngleRoll",
                "AngRateX","AngRateY","AngRateZ",
                "AngRateForward ","AngRateLateral",
                "DistanceWithHold","Distance ",
                "PosLocalX","PosLocalY",
                "VelLocalX","VelLocalY","AngleLocalYaw ","AngleLocalTrack",
                "AngAccelForward °/s²","AngAccelLateral °/s²"


            ])

            lineNumber = 0
            for s in lines:
                lineNumber += 1
                s = s.strip()
                # 跳过空行或以 ';' 开头的注释行
                if not s or s.startswith(';'):
                    continue
                # 按 C# 代码逻辑：仅处理第 22 行及以后且长度大于 40 的行
                if lineNumber < 21 or len(s) <= 40:
                    continue

                try:
                    msg = CANMessageInfo(s)
                except Exception as e:
                    print(f"解析第 {lineNumber} 行时出错: {s}\n错误信息: {e}")
                    continue

#####################################################################################
                if msg.messageId == 0x600:
                    msg.timeMs = msg.GetTimeMs()
                    if not ifTimeMessage:
                        ifTimeMessage = True
                        # 调整之前所有消息的时间戳
                        for m in self.messageList:
                            m.timeMs = msg.timeMs - (msg.timeOffset - m.timeOffset)
                    lastTimeMessage = msg
                elif ifTimeMessage and lastTimeMessage is not None:
                    msg.timeMs = (lastTimeMessage.timeMs +
                                  (msg.timeOffset - lastTimeMessage.timeOffset))

                self.messageList.append(msg)
#####################################################################################
                # # 如果消息 ID 为 0x601，则用 payload 中的数据更新 Pos
                if msg.messageId == 0x601 and len(msg.payload) >= 2:
                        PosLon  = msg.GetFloats(offset=4,factor=1e-7,fmt=4)
                        PosLat  = msg.GetFloats(offset=0,factor=1e-7,fmt=4)
                else:
                    PosLon  = "N/A"
                    PosLat  = "N/A"
#####################################################################################
                if msg.messageId == 0x602 and len(msg.payload) >= 2:
                        Altitude  = msg.GetFloats(offset=0,factor=0.001,fmt=4)
                else:
                    Altitude  = "N/A"
#####################################################################################
                if msg.messageId == 0x603 and len(msg.payload) >= 2:
                        Speed2D = msg.GetFloats(offset=6,factor=0.01,fmt=2)
                else:
                    Speed2D  = "N/A"
#####################################################################################
                if msg.messageId == 0x60E and len(msg.payload) >= 2:
                        AngAccelX = msg.GetFloats(offset=0,factor=0.1,fmt=2)
                        AngAccelY = msg.GetFloats(offset=2,factor=0.1,fmt=2)
                        AngAccelZ = msg.GetFloats(offset=4,factor=0.1,fmt=2)
                else:
                    AngAccelX  = "N/A"
                    AngAccelY  = "N/A"
                    AngAccelZ  = "N/A"
#####################################################################################
                if msg.messageId == 0x604 and len(msg.payload) >= 2:
                        VelForward = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        VelLateral  = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                else:
                    VelForward  = "N/A"
                    VelLateral = "N/A"
#####################################################################################
                if msg.messageId == 0x605 and len(msg.payload) >= 2:
                        AccelX  = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        AccelY  = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                        AccelZ  = msg.GetFloats(offset=4,factor=0.01,fmt=2)
                else:
                    AccelX  = "N/A"
                    AccelY  = "N/A"
                    AccelZ  = "N/A"
#####################################################################################
                if msg.messageId == 0x606 and len(msg.payload) >= 2:
                        AccelForward  = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        AccelLateral  = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                        AccelSlip   = msg.GetFloats(offset=6,factor=0.01,fmt=2)
                else:
                    AccelForward  = "N/A"
                    AccelLateral  = "N/A"
                    AccelSlip   = "N/A"
#####################################################################################
                if msg.messageId == 0x607 and len(msg.payload) >= 2:
                        AngleHeading  = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        AnglePitch  = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                        AngleRoll    = msg.GetFloats(offset=4,factor=0.01,fmt=2)
                else:
                    AngleHeading  = "N/A"
                    AnglePitch  = "N/A"
                    AngleRoll    = "N/A"
#####################################################################################
                if msg.messageId == 0x608 and len(msg.payload) >= 2:
                        AngRateX  = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        AngRateY  = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                        AngRateZ  = msg.GetFloats(offset=4,factor=0.01,fmt=2)
                else:
                    AngRateX  = "N/A"
                    AngRateY  = "N/A"
                    AngRateZ  = "N/A"
#####################################################################################
                if msg.messageId == 0x609 and len(msg.payload) >= 2:
                        AngRateForward   = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        AngRateLateral   = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                else:
                    AngRateForward  = "N/A"
                    AngRateLateral   = "N/A"
#####################################################################################
                if msg.messageId == 0x60B and len(msg.payload) >= 2:
                        DistanceWithHold = msg.GetFloats(offset=0,factor=0.001,fmt=2)
                        Distance= msg.GetFloats(offset=4,factor=0.001,fmt=2)
                else:
                    DistanceWithHold  = "N/A"
                    Distance  = "N/A"
#####################################################################################
                if msg.messageId == 0x60C and len(msg.payload) >= 2:
                        PosLocalX = msg.GetFloats(offset=0,factor=0.0001,fmt=4)
                        PosLocalY = msg.GetFloats(offset=4,factor=0.0001,fmt=4)
                else:
                    PosLocalX  = "N/A"
                    PosLocalY  = "N/A"
#####################################################################################
                if msg.messageId == 0x60D and len(msg.payload) >= 2:
                        VelLocalX  = msg.GetFloats(offset=0,factor=0.01,fmt=2)
                        VelLocalY = msg.GetFloats(offset=2,factor=0.01,fmt=2)
                        AngleLocalYaw  = msg.GetFloats(offset=4,factor=0.01,fmt=2)
                        AngleLocalTrack = msg.GetFloats(offset=6,factor=0.01,fmt=2)
                else:
                    VelLocalX  = "N/A"
                    VelLocalY  = "N/A"
                    AngleLocalYaw  = "N/A"
                    AngleLocalTrack  = "N/A"
#####################################################################################
                if msg.messageId == 0x60F and len(msg.payload) >= 2:
                        AngAccelForward  = msg.GetFloats(offset=0,factor=0.1,fmt=2)
                        AngAccelLateral  = msg.GetFloats(offset=2,factor=0.1,fmt=2)
                else:
                    AngAccelForward   = "N/A"
                    AngAccelLateral   = "N/A"
                # 写入 CSV 一行
                writer.writerow([
                    msg.messageNumber,
                    msg.timeOffset,
                    hex(msg.messageId),
                    msg.length,
                    ' '.join(f"{b:02X}" for b in msg.payload),
                    msg.timeMs,
                    msg.timeString,
                    PosLon,PosLat,
                    Altitude,
                    Speed2D,
                    AngAccelX,AngAccelY,AngAccelZ,
                    VelForward,VelLateral, 
                    AccelX,AccelY,AccelZ,
                    AccelForward ,AccelLateral,AccelSlip, 
                    AngleHeading,AnglePitch,AngleRoll, 
                    AngRateX,AngRateY,AngRateZ,
                    AngRateForward,AngRateLateral,
                    DistanceWithHold,Distance,
                    PosLocalX,PosLocalY,
                    VelLocalX,VelLocalY,AngleLocalYaw,AngleLocalTrack,
                    AngAccelForward,AngAccelLateral  
    
                ])

        print(f"解析完成，结果已写入: {csv_filename}")

    @property
    def messageCount(self):
        return len(self.messageList)

    def GetMessageList(self, id=None):
        """
        若不传入 id，返回所有消息；  
        若传入 id，则返回 messageId 等于该 id 的消息列表，若无则返回 None。
        """
        if id is None:
            return self.messageList
        filtered = [m for m in self.messageList if m.messageId == id]
        return filtered if filtered else None

    def GetBreakLight(self):
        """
        针对消息 ID 为 0x570 的消息，重新计算 timeMs：  
          payload[0]*3600000 + payload[1]*60000 + (payload[2,3] 按 UInt16 解析)
        """
        breakLightMessageList = self.GetMessageList(0x570)
        if breakLightMessageList:
            for m in breakLightMessageList:
                if len(m.payload) >= 4:
                    val = struct.unpack_from('<H', m.payload, 2)[0]
                    m.timeMs = (m.payload[0] * 3600000 +
                                m.payload[1] * 60000 +
                                val)
        return None


# --------------------- 以下为“缺失的 C# 部分”对应的 Python 实现 ---------------------

class PointCarrier:
    """
    对应 C# 的 PointCarrier，用于记录时间、位置、速度、积分位置等信息。
    """
    def __init__(self, time_val, position, speed, position_integration=0.0):
        """
        :param time_val:   时间（毫秒）
        :param position:   当前位置
        :param speed:      当前速度
        :param position_integration: 累计积分位置
        """
        self.time = time_val
        self.position = position
        self.speed = speed
        self.positionIntegration = position_integration
        self.timeString = self._time2string()

    def _time2string(self):
        """
        将 self.time（毫秒）转换为 "hour:minute:second:ms" 字符串，
        与 C# 代码逻辑保持一致。
        """
        hour = self.time // 3600000
        remainder = self.time % 3600000
        minute = remainder // 60000
        remainder = remainder % 60000
        second = remainder // 1000
        ms = remainder % 1000
        return f"{hour}:{minute}:{second}:{ms}"


class LocalMessage:
    """
    对应 C# 的 LocalMessage，用于读取本地文件 (time, position, speed)
    并做积分计算，保存为一系列 PointCarrier。
    """
    def __init__(self, fileName):
        """
        C# 逻辑：
         1) 读取整个文件的字节数组，将冒号 ':' 替换为 '.' 并写回文件
         2) 逐行读取，拆分为 time, position, speed
         3) 第一次行将 position 直接存入 positionIntegration，其后用梯形法积分
         4) time = hour*3600000 + minute*60000 + second*1000 + 17000 (与 C# 一致)
        """
        # 1) 替换 ':' 为 '.'
        if os.path.isfile(fileName):
            with open(fileName, 'rb') as f:
                dataArray = bytearray(f.read())

            for i in range(len(dataArray)):
                if dataArray[i] == ord(':'):
                    dataArray[i] = ord('.')

            with open(fileName, 'wb') as f:
                f.write(dataArray)

        self.points = []
        speedPre = 0.0
        positionSum = 0.0
        timePre = 0
        lineNumber = 0

        # 2) 逐行读取，解析 time, position, speed
        with open(fileName, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # 期望格式: "HH.MM.SS, position, speed"
                # C# 中是用逗号分隔
                parts = line.split(',')
                if len(parts) < 3:
                    continue

                time_str = parts[0].strip()
                pos_str = parts[1].strip()
                speed_str = parts[2].strip()

                # time_str 再按 '.' 分割: [hour, minute, second]
                time_tokens = time_str.split('.')
                if len(time_tokens) < 3:
                    continue

                hour = int(time_tokens[0])
                minute = int(time_tokens[1])
                second = int(time_tokens[2])
                # 与 C# 代码一致，多加 17000 毫秒
                time_val = hour * 3600000 + minute * 60000 + second * 1000 + 17000

                position = float(pos_str)
                speed = float(speed_str)

                # 3) 积分计算
                if lineNumber == 0:
                    # 第一行：positionIntegration = 当前 position
                    self.points.append(PointCarrier(time_val, position, speed, position))
                else:
                    # 梯形法积分
                    dt = (time_val - timePre)  # 毫秒
                    positionSum += ((speed + speedPre) * dt / 2000.0)  # ( /1000 * /2)
                    self.points.append(PointCarrier(time_val, position, speed, positionSum))

                speedPre = speed
                timePre = time_val
                lineNumber += 1


class MessageDecode:
    """
    对应 C# 的 MessageDecode，用于组合 CAN 数据 (CANMessage) 与本地数据 (LocalMessage)。
    """
    def __init__(self, fileCan, fileLocal):
        """
        C# 逻辑：
          canData = new CANMessage(file1)
          carrierData = new LocalMessage(file2)
          canData.messageList.Sort(...) 根据 timeMs 排序
        """
        self.canData = CANMessage(fileCan)
        self.carrierData = LocalMessage(fileLocal)
        # 按时间排序 CAN 消息
        self.canData.messageList.sort(key=lambda m: m.timeMs)




if __name__ == '__main__':
    # 设置一级目录路径（例如：包含多个文件夹的顶级目录）
    root_dir = r"C:\Users\17845\Desktop\子刊讨论\Mannequin Test Dataset"
    
    # 使用 os.walk 遍历所有子目录
    for current_dir, sub_dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.trc'):
                trc_file = os.path.join(current_dir, file)
                print(f"正在处理文件: {trc_file}")
                try:
                    # 处理 .trc 文件，生成 CSV 文件会保存在 trc_file 同一目录下
                    can_data = CANMessage(trc_file)
                    print(f"处理完成：{trc_file} 共 {can_data.messageCount} 条 CAN 消息。")
                except Exception as e:
                    print(f"处理 {trc_file} 时出错: {e}")
