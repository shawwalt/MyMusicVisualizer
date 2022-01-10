from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

# 创建 绘制窗口类 PlotWindow 对象，内置一个绘图控件类 PlotWidget 对象
pw = pg.plot()

# 背景色改为白色
pw.setBackground('w')

# 显示表格线
pw.showGrid(x=False, y=False)

# 设置Y轴 刻度 范围
pw.setYRange(
    min=0,  # 最小值
    max=65535)  # 最大值

pw.setXRange(
    min=0,
    max=22050
)

QtGui.QApplication.instance().exec_()