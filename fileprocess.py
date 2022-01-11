from scipy.fft import rfft, rfftfreq
import numpy as np
import struct
import wave


# 这是一个文件处理类的接口定义
class FileProcessor(object):
    def __init__(self, path, filename):
        self.path = path  # 文件的存放目录
        self.filename = filename  # 文件全名
        self.path_t = path + '\\' + filename  # 完整文件路径

    def file_read(self):  # 读取文件内容并返回数据
        pass

    def fft_data(self):  # 对返回数据进行fft变换
        pass


# 这是专门用于处理.wav文件的类
class WavProcessor(FileProcessor):
    def __init__(self, path, filename):
        super().__init__(path, filename)
        self.nchannels = -1
        self.sampwidth = -1
        self.framerate = -1
        self.nframes = -1
        self.file_read()

    def file_read(self):
        #  打开文件并读取
        try:
            f = wave.open(self.path_t)
            params = f.getparams()
            nchannels, sampwidth, framerate, nframes = params[:4]
            self.nchannels = nchannels  # 采样通道数
            self.sampwidth = sampwidth  # 采样字节长度，例如2即表示一个采样点的数据大小2byte==16bit
            self.framerate = framerate  # 采样率，即每秒中数据包含的采样点个数
            self.nframes = nframes  # 文件包含的采样点总个数
            self.raw_data = f.readframes(nframes)  # 从文件中直接读取未经处理的二进制数据
            self.transferred_data = self.byte2int()  # 经过格式转换后可以做进一步数学处理的数据
            f.close()
        except FileNotFoundError:
            print('file not found')
            return None

    #  将二进制数据转换成整型
    def byte2int(self) -> np.array:
        #  采样通道数为2时的处理方式
        if self.nchannels == 2:
            # byte to short(size=2*8bit)
            transferred_data = np.frombuffer(self.raw_data, np.short)
            # 由于是双声道，所以list中的奇数采样点为左声道，其余为右声道
            # 所以将原始数据先转为两列，转置后为list[0]为左声道，list[1]为右声道
            transferred_data.shape = -1, 2
            transferred_data = transferred_data.T
            left_track = transferred_data[0]
            right_track = transferred_data[1]
            time = np.arange(0, self.nframes) * (1.0 / self.framerate)
            return np.array([left_track, right_track, time])
        else:
            # 其余情况的处理方式日后优化
            print('not 2 channels wav file')
            return None

    #  对数据做fft处理并返回处理后的list
    #  传入参数为fft数据的起始时刻和终止时刻(s)
    #  目前只支持传入整型
    def fft_data(self, start_time: int, end_time: int):
        #  将时刻转为对应的索引
        start_point = start_time * self.framerate
        end_point = end_time * self.framerate

        left_track = self.transferred_data[0]
        right_track = self.transferred_data[1]

        # 对整个索引做切片，取出要做fft的部分
        left_segment = left_track[start_point:end_point]
        right_segment = right_track[start_point:end_point]

        # N为fft部分的采样点个数
        N = end_point - start_point
        # 生成fft的x,y轴
        xf = rfftfreq(N, 1 / self.framerate)
        yf_left = rfft(left_segment)
        yf_right = rfft(right_segment)
        return [yf_left, yf_right, xf]


if __name__ == "__main__":
    wd = WavProcessor('.\\MUSIC', 'killingMe.wav')
    wd.fft_data(100, 102)