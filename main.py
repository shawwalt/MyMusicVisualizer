from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist, QMediaPlayer
from PyQt5.QtGui import QFont, QIcon
from pyqtgraph import PlotWidget
from PyQt5.QtCore import QSize, QTimer, QUrl
from visualizer import Ui_MainWindow
from fileprocess import WavProcessor

import os
import sys
import time
import numpy as np


# 绘制音频动态图像的控件
class MyPlotter(PlotWidget):
    def __init__(self, x_range, y_range):
        self.x_range = x_range
        self.y_range = y_range
    
    # 设置控件x,y轴的数据
    def line_plot(self, x_data, y_data):
        self.plot(x_data, y_data)


# 程序主窗口
class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.cur_song = ''  # 当前加载歌曲名
        self.cur_song_list = []  # 当前文件目录中的歌曲列表
        self.is_pause = True  # 标记播放状态
        self.setupUi(self)
        self.initialize()

    def initialize(self):
        self.setWindowTitle("炫音播放器")
        self.setWindowIcon(QIcon('.resource/windowTitleIcon.jfif'))
        self.lb_current_time.setText("0:00")
        self.lb_current_loading_file.setText("当前无正在播放歌曲")
        ft = QFont()
        ft.setPointSize(14)
        self.lb_current_loading_file.setFont(ft)
        self.pb_stop_or_start.setIcon(QIcon('.resource/start_audio.jfif'))
        self.pb_stop_or_start.setIconSize(QSize(32, 32))

        self.playlist = QMediaPlaylist()  # 播放列表
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)  # 列表默认播放状态
        self.player = QMediaPlayer(self)  # 播放器
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(50)

        # 设置控件绑定
        self.pb_open_file_dir.clicked.connect(
            lambda: self.pb_open_file_clicked())
        
        # 为防止拖动进度条时由于音频仍在播放而产生噪音，先暂停播放
        # 然后在松开控件是继续当前位置播放
        # 因此利用了三个信号
        self.slide_time.sliderPressed.connect(lambda: self.player.pause())
        self.slide_time.sliderMoved[int].connect(
            lambda: self.player.setPosition(self.slide_time.value()))
        self.slide_time.sliderReleased.connect(lambda: self.player.play())

        self.cb_music_list.currentIndexChanged.connect(
            lambda: self.cb_music_list_indexChange(self.cb_music_list.
                                                   currentIndex()))
        self.pb_stop_or_start.clicked.connect(
            lambda: self.pb_stop_or_start_control())

        # 计时器:控制进度条和进度时间
        self.timer = QTimer(self)
        self.timer.start(200)
        self.timer.timeout.connect(self.player_timer)

        # 音乐可视化
        self.visualize_init()

    def pb_open_file_clicked(self):
        self.playlist.clear()  # 读取歌曲前，清空playlist
        list = []
        dir_of_music = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if len(dir_of_music) == 0:
            print('未选择')
            return
        else:
            # 返回完整文件路径列表
            list = self.search_dir(dir_of_music)
            # 更新comboBox内内容
            self.cb_music_list.clear()
            for m in list:
                base_name = os.path.basename(m)
                self.cb_music_list.addItem(base_name)
        #  默认播放第一首歌
        self.playlist.addMedia(
            QMediaContent(QUrl.fromLocalFile(self.cur_song_list[0])))

    # 查找选中目录下所有的mp3\wav文件
    def search_dir(self, directory: str):
        list = []
        g = os.walk(directory)
        for path, d, files in g:
            for filename in files:
                file = path + '/' + filename
                if 'wav' in file:
                    list.append(file)
                if 'mp3' in file:
                    list.append(file)
        # 更新完整歌曲路径存储列表
        self.cur_song_list = list
        # 更改当前播放歌曲的显示控件
        self.lb_current_loading_file.setText(self.cb_music_list.currentText())
        return list

    # 控制播放的开始和停止
    def pb_stop_or_start_control(self):
        if self.is_pause is True:
            self.is_pause = False
            self.player.play()
            self.pb_stop_or_start.setIcon(QIcon('.resource/stop_audio.jfif'))
        else:
            self.is_pause = True
            self.player.pause()
            self.pb_stop_or_start.setIcon(QIcon('.resource/start_audio.jfif'))

    # 切歌时的反应
    def cb_music_list_indexChange(self, index):
        # 暂停播放器
        self.player.pause()
        self.is_pause = True
        # 清空播放列表
        self.playlist.clear()
        # 获取当前播放歌曲名称，添加歌曲到列表，重设时间显示
        self.lb_current_loading_file.setText(self.cb_music_list.currentText())
        self.playlist.addMedia(
            QMediaContent(
                QUrl(self.cur_song_list[self.cb_music_list.currentIndex()])))
        self.pb_stop_or_start.setIcon(QIcon('.resource/start_audio.jfif'))
        self.playlist.addMedia(QMediaContent(QUrl(self.cur_song_list[index])))
        self.cur_song = self.cb_music_list.currentText()
        self.lb_current_time.setText(
            time.strftime('%M:%S',
                          time.localtime(self.player.position() / 1000)))

    #  设置进度条和播放时间
    def player_timer(self):
        cur_time = time.strftime('%M:%S',
                                 time.localtime(self.player.position() / 1000))
        self.slide_time.setMinimum(0)
        self.slide_time.setMaximum(self.player.duration())
        self.slide_time.setValue(self.player.position())

        self.lb_current_time.setText(cur_time)

        # 进度条满了之后回零
        if self.player.duration() == self.slide_time.value():
            self.slide_time.setValue(0)

    def load_wav(self):
        path_t = self.cur_song_list[self.cb_music_list.currentIndex()]
        path, filename = os.path.split(path_t)
        print(path, filename)
        self.wav_processor = WavProcessor(path, filename)

    def visualize_init(self):
        x_range = [0, self.wav_processor.framerate / 2]
        y_range = [0, np.iinfo(np.short).max]
        self.my_plot = MyPlotter(x_range, y_range)
        self.GraphLayout.addWidget(self.my_plot)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())