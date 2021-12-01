
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import GraphicsLayoutWidget
import pyqtgraph as pg
import numpy as np
from detectors_info import *
from PyQt5.QtCore import QObject, Qt



class Ui_BlackBirdPanel(object):
    def setupUi(self, BlackBirdPanel_MainWindow):  # 主函数中的窗体会继承此类，并会把本身（self）传入作为入参
        BlackBirdPanel_MainWindow.setObjectName('BlackBirdPanel_MainWindow')
        BlackBirdPanel_MainWindow.resize(1800,900)  # 缩放主窗体大小
        # BlackBirdPanel_MainWindow.showFullScreen()
        self.centralwidget = QtWidgets.QFrame(BlackBirdPanel_MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget) 

##################################################################
#######################  创建基本模块  ############################

        """"左侧的信号列表"""
        self.tw = QtWidgets.QTabWidget(self)
        
        # self.signalTable = QtWidgets.QTableWidget()
        # self.signalTable.setObjectName("signalTable")
        # # 设定初始的行数和列数
        # self.signalTable.setColumnCount(4)
        # self.signalTable.setRowCount(20)
        # self.signalTable.setHorizontalHeaderLabels(['中心频率\n(MHz)', '带宽\n(kHz)', '功率\n(dBm)', '信号体制'])
        # # 表头尺寸自动拉伸
        # self.signalTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.signalTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # # 设置表头文字的颜色
        # self.signalTable.horizontalHeader().setStyleSheet("color: rgb(0, 83, 128);")
        # self.signalTable.verticalHeader().setStyleSheet("color: rgb(0, 83, 128);")
        # # 整个横向表头字体加粗
        # font = self.signalTable.horizontalHeader().font()
        # font.setBold(True)
        # self.signalTable.horizontalHeader().setFont(font)   # 是指整个横向表头

        self.signalTable1 = self.creatSignaltable()
        self.signalTable2 = self.creatSignaltable()
        self.signalTable3 = self.creatSignaltable()

        #signalTable1 = self.creatSignaltable(self)

        self.tw.addTab(self.signalTable1, '所有信号')
        self.tw.addTab(self.signalTable2, '备案信号')
        self.tw.addTab(self.signalTable3, '未知信号')

        """右上区域各类按钮"""
        self.top_right_container = QtWidgets.QFrame()
        self.top_right_container.setFrameShape(QtWidgets.QFrame.Box)
        self.top_right_layout = QtWidgets.QGridLayout(self.top_right_container)
        self.start_button = QtWidgets.QPushButton('手动刷新')
        self.autoRefresh = QtWidgets.QPushButton('自动刷新')
        self.checkall_button = QtWidgets.QPushButton('全选')
        self.uncheckall_button = QtWidgets.QPushButton('全取消')
        self.chooseHistoryBtn = QtWidgets.QPushButton('选择历史')

        self.top_right_layout.addWidget(self.start_button,0,0)
        self.top_right_layout.addWidget(self.autoRefresh,1,0)
        self.top_right_layout.addWidget(self.checkall_button,2,0)
        self.top_right_layout.addWidget(self.uncheckall_button,3,0)
        self.top_right_layout.addWidget(self.chooseHistoryBtn,4,0)


        self.scroll = QtWidgets.QScrollArea()   # 创建一个滚动区域用来容纳check box
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout()
        self.checkbox_lists = []
        for i in range(30):
            ck_box = QtWidgets.QCheckBox(detectors_name_lists[i])
            self.checkbox_lists.append(ck_box)
            scroll_layout.addWidget(ck_box)
        scroll_widget.setLayout(scroll_layout)
        self.scroll.setWidget(scroll_widget)
        self.top_right_layout.addWidget(self.scroll,0,1,4,2)

        

        
        """右下区域的绘图"""
        self.bottom_right_container = QtWidgets.QFrame()
        self.bottom_right_container.setFrameShape(QtWidgets.QFrame.Box)
        self.bottom_right_container_layout = QtWidgets.QHBoxLayout(self.bottom_right_container)

        self.pg_layout_widget = GraphicsLayoutWidget(self.bottom_right_container)  # 此函数返回一个widget类型对象，不是layout类型
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pg_layout_widget.sizePolicy().hasHeightForWidth())
        self.pg_layout_widget.setSizePolicy(sizePolicy)
        self.pg_layout_widget.setObjectName("signalPlotLayout")

        self.bottom_right_container_layout.addWidget(self.pg_layout_widget)

        self.bottom_right_posLabel= self.pg_layout_widget.addLabel(row=0, col=0, justify="right")
        self.bottom_right_plot = self.pg_layout_widget.addPlot(row=1, col=0)

        self.bottom_right_plot.showGrid(x=True, y=True)
        self.bottom_right_plot.setLabel("left", "Power", units="dB")
        self.bottom_right_plot.setLabel("bottom", "Frequency", units="Hz")
        self.bottom_right_plot.setLimits(xMin=0)
        self.bottom_right_plot.showButtons()
        self.bottom_right_plot.addLegend(size=(100,30))

        self.bottom_right_plot.setXRange(20e6,5.8e9)
        self.bottom_right_plot.setYRange(-100,-20)

        noise_baseline = self.bottom_right_plot.plot(pen=pg.mkColor('w'))
        noise_value = BlackBirdPanel_MainWindow.noise_value
        noise_baseline.setData(np.linspace(20e6,6e9,100), [noise_value]*100)   # 这里应该根据监测软件使用的噪声电平值来设定
        self.bottom_right_plot.setLimits(maxXRange=6e9,minYRange=-120)

        self.main_color = pg.mkColor("y")
        self.curve = self.bottom_right_plot.plot(pen=self.main_color)
        self.curve.setZValue(900)

##################################################################
#######################  主窗体布局设计  ############################

        # 创建竖直和水平的分割线  Horizontal  Vertical
        vert_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal) #竖直分割器的布局是水平的，而不是竖直的，下同
        hori_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)



        # 主窗体的左侧为信号列表
        vert_splitter.addWidget(self.tw)
        vert_splitter.addWidget(hori_splitter)

        vert_splitter.setStretchFactor(0,2) # 设定分割线左侧宽度2个单位，右侧宽度1个单位
        vert_splitter.setStretchFactor(1,1)

        # 主窗体的右侧上半部分是操作按钮，下半部分是绘图区域
        hori_splitter.addWidget(self.top_right_container)
        hori_splitter.addWidget(self.bottom_right_container)
        
        self.horizontalLayout.addWidget(vert_splitter)
        BlackBirdPanel_MainWindow.setCentralWidget(self.centralwidget)
    
    def creatSignaltable(self):
        self.signalTable = QtWidgets.QTableWidget()
        self.signalTable.setObjectName("signalTable")
        # 设定初始的行数和列数
        self.signalTable.setColumnCount(4)
        self.signalTable.setRowCount(40)
        self.signalTable.setHorizontalHeaderLabels(['中心频率', '带宽', '功率', '备案信息'])
        # 表头尺寸自动拉伸

        self.signalTable.horizontalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
        self.signalTable.horizontalHeader().setSectionResizeMode(1,QtWidgets.QHeaderView.Stretch)
        self.signalTable.horizontalHeader().setSectionResizeMode(2,QtWidgets.QHeaderView.Stretch)
        self.signalTable.setColumnWidth(3,400)  # 第三列设置的宽一点
        self.signalTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.signalTable.verticalHeader().setDefaultSectionSize(40)


        # self.signalTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # 设置表头文字的颜色
        self.signalTable.horizontalHeader().setStyleSheet("color: rgb(0, 83, 128);")
        self.signalTable.verticalHeader().setStyleSheet("color: rgb(0, 83, 128);")
        # 整个横向表头字体加粗
        font = self.signalTable.horizontalHeader().font()
        font.setBold(True)
        self.signalTable.horizontalHeader().setFont(font)   # 是指整个横向表头
        self.signalTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.signalTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.signalTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) #不允许编辑
        self.signalTable.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        
        return self.signalTable

    