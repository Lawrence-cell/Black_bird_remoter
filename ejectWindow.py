from PyQt5 import QtCore, QtGui, QtWidgets
# from pyqtgraph import GraphicsLayoutWidget
# import pyqtgraph as pg
import numpy as np
from detectors_info import *
from PyQt5.QtCore import QObject, Qt


class ejectWindow(object):
    def setupUi(self, BlackBirdPanel_MainWindow):  # 主函数中的窗体会继承此类，并会把本身（self）传入作为入参
        BlackBirdPanel_MainWindow.setObjectName('BlackBirdPanel_MainWindow')
        BlackBirdPanel_MainWindow.resize(900,450)  # 缩放主窗体大小
        # BlackBirdPanel_MainWindow.showFullScreen()
        self.centralwidget = QtWidgets.QFrame(BlackBirdPanel_MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget) 
        self.historyRecord = self.creatSignaltable()
        self.horizontalLayout.addWidget(self.historyRecord)
        BlackBirdPanel_MainWindow.setCentralWidget(self.centralwidget)
    
    def creatSignaltable(self):
        self.signalTable = QtWidgets.QTableWidget()
        self.signalTable.setObjectName("signalTable")
        # 设定初始的行数和列数
        self.signalTable.setColumnCount(1)
        self.signalTable.setRowCount(4)
        self.signalTable.setHorizontalHeaderLabels(['历史记录'])
        # 表头尺寸自动拉伸
        self.signalTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.signalTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # 设置表头文字的颜色
        self.signalTable.horizontalHeader().setStyleSheet("color: rgb(0, 83, 128);")
        self.signalTable.verticalHeader().setStyleSheet("color: rgb(0, 83, 128);")
        # 整个横向表头字体加粗
        font = self.signalTable.horizontalHeader().font()
        font.setBold(True)
        self.signalTable.horizontalHeader().setFont(font)   # 是指整个横向表头
        self.signalTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.signalTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.signalTable.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.signalTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        return self.signalTable



class test_taowa(QtWidgets.QMainWindow, ejectWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

# class ejectWindow(QtWidgets.QDialog):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
 
#     def initUI(self):
#         self.resize(400, 400)
#         self.child_widget = QtWidgets.QFrame()
#         self.layout = QtWidgets.QHBoxLayout(self.child_widget) 
#         self.test_btn = QtWidgets.QPushButton('test')
#         self.layout.addWidget(self.test_btn)

#         # self.setWindowFlags(Qt.WindowCloseButtonHint)
#         # self.setWindowTitle('选择历史数据')
#         # self.resize(400, 400)
        
#         # self.container = QtWidgets.QFrame()
#         # self.container.setFrameShape(QtWidgets.QFrame.Box)
#         # self.layout = QtWidgets.QGridLayout(self.container)

#         # self.data_Table = QtWidgets.QTableWidget()
#         # self.data_Table.setObjectName("data_Table")
#         # # 设定初始的行数和列数
#         # self.data_Table.setColumnCount(5)
#         # self.data_Table.setRowCount(20)
#         # self.data_Table.setHorizontalHeaderLabels(['中心频率\n(MHz)', '带宽\n(kHz)', '功率\n(dBm)', '信号体制','备案信息'])
#         # # 表头尺寸自动拉伸
#         # self.data_Table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
#         # self.data_Table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
#         # # 设置表头文字的颜色
#         # self.data_Table.horizontalHeader().setStyleSheet("color: rgb(0, 83, 128);")
#         # self.data_Table.verticalHeader().setStyleSheet("color: rgb(0, 83, 128);")
#         # # 整个横向表头字体加粗
#         # font = self.data_Table.horizontalHeader().font()
#         # font.setBold(True)
#         # self.data_Table.horizontalHeader().setFont(font)   # 是指整个横向表头
#         # self.data_Table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
#         # self.data_Table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
#         # self.layout.addWidget(self.data_Table,0,0)
        
