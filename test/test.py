# import numpy as np

# list = np.array([[1, 2, 3, 4], [2, 4, 6, 8]])
# list = list[:, 0] + list[:, 1]
# print(list)

# print(31772716 * 8 / 44100 / 16 / 2)
def wav_read(self):
        f = wave.open(self.path_t, "rb")
        # 一次性返回所有的WAV文件的格式信息，它返回的是一个组元(tuple)：声道数, 量化位数（byte单位）,
        # 采样频率, 采样点数, 压缩类型, 压缩类型的描述。wave模块只支持非压缩的数据，因此可以忽略最后两个信息'''
        params = f.getparams()
        print(params)
        # 读取波形数据
        nchannels, sampwidth, framerate, nframes = params[:4]
        # 读取声音数据，传递一个参数指定需要读取的长度（以取样点为单位）
        str_data = f.readframes(nframes)
        print(len(str_data))
        f.close()
        # 需要根据声道数和量化单位，将读取的二进制数据转换为一个可以计算的数组
        wave_data = np.frombuffer(str_data, dtype=np.short)
        print(type(wave_data))
        print(len(wave_data))
        # 将wave_data数组改为2列，行数自动匹配。在修改shape的属性时，需使得数组的总长度不变。
        wave_data.shape = -1, 2
        # 转置数据,使成为2行的数据，方便下面时间匹配
        wave_data = wave_data.T
        # 通过取样点数和取样频率计算出每个取样的时间,也就是周期T=采样单数/采样率
        time = np.arange(0, nframes) * (1.0 / framerate)
        return wave_data, time

    def data_fft(self, data, time, start, end):
        # wavedata, wavetime = wave_read(path)
        t = []
        y = []
        for i in range(time.size):
            if ((time[i] >= start) & (time[i] <= end)):
                t = np.append(t, time[i])
                y = np.append(y, data[0][i])  # 取左声道
        n = len(t)  # 信号长度
        yy = fft(y)
        yf = abs(yy)  # 取绝对值
        yf1 = abs(fft(y)) / n  # 归一化处理
        yf2 = yf1[range(int(n / 2))]  # 由于对称性，只取一半区间

        xf = np.arange(len(y))  # 频率
        xf1 = xf
        xf2 = xf[range(int(n / 2))]  # 取一半区间

        # 显示原始序列
        plt.figure()
        plt.subplot(221)
        plt.plot(t, y, 'g')
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.title("Original wave")

        # 显示取绝对值后的序列
        plt.subplot(222)
        plt.plot(xf, yf)
        plt.xlabel("Freq (Hz)")
        plt.ylabel("|Y(freq)|")
        plt.title("FFT of Mixed wave(two sides frequency range",
                  fontsize=7,
                  color='#7A378B')
        # 注意这里的颜色可以查询颜色代码表

        # 显示归一化处理后双边序列
        plt.subplot(223)
        plt.plot(xf1, yf1)
        # 注意这里的颜色可以查询颜色代码表
        plt.xlabel("Freq (Hz)")
        plt.ylabel("|Y(freq)|")
        plt.title('FFT of Mixed wave(Normalized processing)',
                  fontsize=10,
                  color='#F08080')

        # 显示归一化处理后单边序列
        plt.subplot(224)
        plt.plot(xf2, yf2, 'b')
        # 注意这里的颜色可以查询颜色代码表
        plt.xlabel("Freq (Hz)")
        plt.ylabel("|Y(freq)|")
        plt.title('FFT of Mixed wave', fontsize=10, color='#F08080')

        plt.show()

        # test  source: https://blog.csdn.net/taw19960426/article/details/102502305
    path = 'C:\\Users\\lenovo\\Desktop\\AudioProcessing\\MUSIC'
    filename = 'killingMe.wav'
    fp = FileProcessor(path, filename)
    data, tim = fp.wav_read()
    print(data)
    fp.data_fft(data, tim, 1, 2)

    # 左右声道的显示
    plt.figure()
    plt.subplot(211)
    plt.plot(tim, data[0])
    plt.title("Left channel")
    plt.subplot(212)
    plt.plot(tim, data[1], c="g")
    plt.title("Right channel")
    plt.show()

