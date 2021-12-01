
from PyQt5 import QtCore, QtGui, QtWidgets
#from pyqtgraph import GraphicsLayoutWidget
#import pyqtgraph as pg
import numpy as np
from detectors_info import *
from PyQt5.QtCore import QObject, Qt
# import ctypes
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")



class Ui_BlackBirdPanel(object):
    def setupUi(self, BlackBirdPanel_MainWindow):  # 主函数中的窗体会继承此类，并会把本身（self）传入作为入参
        BlackBirdPanel_MainWindow.setObjectName('BlackBirdPanel_MainWindow')
        BlackBirdPanel_MainWindow.resize(1800,900)  # 缩放主窗体大小
        # BlackBirdPanel_MainWindow.showFullScreen()
        self.centralwidget = QtWidgets.QFrame(BlackBirdPanel_MainWindow)
        self.biggestLayout = QtWidgets.QGridLayout(self.centralwidget) 


##################################################################
#######################  创建基本模块  ############################


        ''''右下部分'''
        

        self.bottom_right_container = QtWidgets.QFrame()
        self.bottom_right_container.setFrameShape(QtWidgets.QFrame.Box)
        self.bottom_right_container.setGeometry(QtCore.QRect(350,50,150,30))
        #self.bottom_right_layout = QtWidgets.QGridLayout(self.bottom_right_container)

        self.startFreLabel = QtWidgets.QLabel(self.bottom_right_container)
        self.startFreLabel.setText("扫频开始频率(MHz)")
        self.startFreLabel.setGeometry(QtCore.QRect(50,50,150,30))
        self.startFrequency = QtWidgets.QTextEdit(self.bottom_right_container)
        self.startFrequency.setGeometry(QtCore.QRect(200,50,200,30))
        self.stopFreLabel = QtWidgets.QLabel(self.bottom_right_container)
        self.stopFreLabel.setText("扫频结束频率(MHz)")
        self.stopFreLabel.setGeometry(QtCore.QRect(450,50,150,30))

        self.stopFrequency = QtWidgets.QTextEdit(self.bottom_right_container)
        self.stopFrequency.setGeometry(QtCore.QRect(600,50,200,30))
      
        self.bootBtn = QtWidgets.QPushButton(self.bottom_right_container)
        self.bootBtn.setText('确定')
        self.bootBtn.setGeometry(QtCore.QRect(50,100,200,30))

        self.start_button = QtWidgets.QPushButton(self.bottom_right_container)
        self.start_button.setText('手动刷新')
        self.start_button.setGeometry(QtCore.QRect(270,100,200,30))

        self.autoRefresh = QtWidgets.QPushButton(self.bottom_right_container)
        self.autoRefresh.setText('自动刷新')
        self.autoRefresh.setGeometry(QtCore.QRect(490,100,200,30))

        self.stopAuto = QtWidgets.QPushButton(self.bottom_right_container)
        self.stopAuto.setText('停止刷新')
        self.stopAuto.setGeometry(QtCore.QRect(710,100,200,30))

    
        
        
        """"左侧的信号列表"""
        
        self.signalTable1 = self.creatSignaltable(1)
        self.signalTable2 = self.creatSignaltable(2)
        self.signalTable3 = self.creatSignaltable(3)
        self.signalTable3.setColumnWidth(0,200)
        self.tw = QtWidgets.QTabWidget(self)
        self.tw.addTab(self.signalTable1, '所有信号')
        self.tw.addTab(self.signalTable2, '备案信号')
        self.tw.addTab(self.signalTable3, '未知信号')
        self.stackedWidget = QtWidgets.QStackedWidget(self)#用于存放多个widget的容器 以供切换不同widget
        
        self.scene_Switch_Container = QtWidgets.QFrame()
        self.scene_Switch_Container.setFrameShape(QtWidgets.QFrame.Box)
        self.scene_Switch_Layout = QtWidgets.QHBoxLayout(self.scene_Switch_Container)


        ######上方的场景选择界面
        self.cb = QtWidgets.QComboBox(self)
        self.cb.addItem('场景一：信号普查')
        self.cb.addItem('场景二：新信号出现')
        self.cb.addItem('场景三：已有信号消失')
        self.cb.addItem('场景四：特定信号检测')
        self.cb.addItem('场景五：特定频率检测')


        # self.scene1_Btn = QtWidgets.QPushButton('场景一：信号普查')
        # self.scene2Btn = QtWidgets.QPushButton('场景二：新信号出现')
        # self.scene3Btn = QtWidgets.QPushButton('场景三：已有信号消失')
        # self.scene4Btn = QtWidgets.QPushButton('场景四：特定信号检测')
        # self.scene5Btn = QtWidgets.QPushButton('场景五：特定频率检测')

        self.scene_Switch_Layout.addWidget(self.cb)
        # self.scene_Switch_Layout.addWidget(self.scene1_Btn)
        # self.scene_Switch_Layout.addWidget(self.scene2Btn)
        # self.scene_Switch_Layout.addWidget(self.scene3Btn)
        # self.scene_Switch_Layout.addWidget(self.scene4Btn)
        # self.scene_Switch_Layout.addWidget(self.scene5Btn)
        
        """"右上部分"""
        self.indexofScene1 = self.stackedWidget.addWidget(self.create_Scene1Widget())
        self.indexofScene2 = self.stackedWidget.addWidget(self.create_Scene2Widget())
        self.indexofScene3 = self.stackedWidget.addWidget(self.create_Scene3Widget())
        self.indexofScene4 = self.stackedWidget.addWidget(self.create_Scene4Widget())
        self.indexofScene5 = self.stackedWidget.addWidget(self.create_Scene5Widget())

        vert_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal) #竖直分割器的布局是水平的，而不是竖直的，下同
        hori_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        # 主窗体的左侧为信号列表
        vert_splitter.addWidget(self.tw)
        vert_splitter.addWidget(hori_splitter)

        vert_splitter.setStretchFactor(0,2) # 设定分割线左侧宽度2个单位，右侧宽度1个单位
        vert_splitter.setStretchFactor(1,1)


        hori_splitter.addWidget(self.stackedWidget)
        hori_splitter.addWidget(self.bottom_right_container)
        
        hori_splitter.setStretchFactor(0,1)
        hori_splitter.setStretchFactor(1,2)

        self.stackedWidget.setCurrentIndex(self.indexofScene1)
        
        self.biggestLayout.addWidget(self.scene_Switch_Container, 0, 0, 1, 10)
        self.biggestLayout.addWidget(vert_splitter, 1, 0, 10, 10)


        BlackBirdPanel_MainWindow.setCentralWidget(self.centralwidget)
    
    def create_Scene1Widget(self):
       
        """右上区域各类按钮"""
        self.scene1Btn = QtWidgets.QPushButton('初始化')
        
        self.checkall_button = QtWidgets.QPushButton('全选')
        self.uncheckall_button = QtWidgets.QPushButton('全取消')
        # self.decideDetectorBtn = QtWidgets.QPushButton('确定')
        self.handoffBtn = QtWidgets.QPushButton('接力')
        self.adjustThreshold = QtWidgets.QPushButton('调节门限')
        

        self.scroll = QtWidgets.QScrollArea()   # 创建一个滚动区域用来容纳check box
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout()
        self.checkbox_lists = []
        self.sequenceLabel = QtWidgets.QLabel('************************以下信号模板按照频率从低到高排列************************')
        scroll_layout.addWidget(self.sequenceLabel)
        for i in range(len(detectors_name_lists)):
            ck_box = QtWidgets.QCheckBox(detectors_name_lists[i])
            self.checkbox_lists.append(ck_box)
            scroll_layout.addWidget(ck_box)
        scroll_widget.setLayout(scroll_layout)
        self.scroll.setWidget(scroll_widget)
        
        self.top_right_container1 = QtWidgets.QFrame()
        self.top_right_container1.setFrameShape(QtWidgets.QFrame.Box)
        self.top_right_layout1 = QtWidgets.QGridLayout(self.top_right_container1)

        self.top_right_layout1.addWidget(self.scene1Btn,0,0)
        self.top_right_layout1.addWidget(self.checkall_button,1,0)
        self.top_right_layout1.addWidget(self.uncheckall_button,2,0)
        self.top_right_layout1.addWidget(self.handoffBtn,3,0)
        self.top_right_layout1.addWidget(self.adjustThreshold,4,0)
        self.top_right_layout1.addWidget(self.scroll,0,1,5,2)
        
        return self.top_right_container1
    
    def create_Scene2Widget(self):
      

        """右上区域各类按钮"""
        self.top_right_container2 = QtWidgets.QFrame()
        self.top_right_container2.setFrameShape(QtWidgets.QFrame.Box)
        self.top_right_layout2 = QtWidgets.QGridLayout(self.top_right_container2)

        self.save_Enviroment_Threshold = QtWidgets.QPushButton('保存当前环境阈值')
        self.load_Environment_Threshold = QtWidgets.QPushButton('选择历史环境阈值载入')
        self.initializeScene2 = QtWidgets.QPushButton('初始化场景')

        self.top_right_layout2.addWidget(self.save_Enviroment_Threshold,0,1)
        self.top_right_layout2.addWidget(self.load_Environment_Threshold,0,2)
        self.top_right_layout2.addWidget(self.initializeScene2,0,0)

        return self.top_right_container2
    

    def create_Scene3Widget(self):
        
        """右上区域各类按钮"""
        self.top_right_container3 = QtWidgets.QFrame()
        self.top_right_container3.setFrameShape(QtWidgets.QFrame.Box)
        self.top_right_layout3 = QtWidgets.QGridLayout(self.top_right_container3)

      
        self.initializeScene3 = QtWidgets.QPushButton('初始化场景')
        
    
        self.top_right_layout3.addWidget(self.initializeScene3, 0, 0)

        return self.top_right_container3
    

    def create_Scene4Widget(self):
        """右上区域各类按钮"""


        self.initializeScene4 = QtWidgets.QPushButton('初始化')
        
        self.checkall_button4 = QtWidgets.QPushButton('全选')
        self.uncheckall_button4 = QtWidgets.QPushButton('全取消')
        # self.decideDetectorBtn = QtWidgets.QPushButton('确定')
        # self.handoffBtn = QtWidgets.QPushButton('接力')
        # self.adjustThreshold = QtWidgets.QPushButton('调节门限')
        

        self.scroll4 = QtWidgets.QScrollArea()   # 创建一个滚动区域用来容纳check box
        scroll_widget4 = QtWidgets.QWidget()
        scroll_layout4 = QtWidgets.QVBoxLayout()
        self.checkbox_lists4 = []
        for i in range(29):
            ck_box = QtWidgets.QCheckBox(mod_lists[i])
            self.checkbox_lists4.append(ck_box)
            scroll_layout4.addWidget(ck_box)
        scroll_widget4.setLayout(scroll_layout4)
        self.scroll4.setWidget(scroll_widget4)
        
        self.top_right_container4 = QtWidgets.QFrame()
        self.top_right_container4.setFrameShape(QtWidgets.QFrame.Box)
        self.top_right_layout4 = QtWidgets.QGridLayout(self.top_right_container4)

        self.top_right_layout4.addWidget(self.initializeScene4,0,0)
        self.top_right_layout4.addWidget(self.checkall_button4,1,0)
        self.top_right_layout4.addWidget(self.uncheckall_button4,2,0)
        # self.top_right_layout4.addWidget(self.handoffBtn,3,0)
        # self.top_right_layout4.addWidget(self.adjustThreshold,4,0)
        self.top_right_layout4.addWidget(self.scroll4,0,4,3,2)
        
        return self.top_right_container4

    def create_Scene5Widget(self):
        """右上区域各类按钮"""


        self.top_right_container5 = QtWidgets.QFrame()
        self.top_right_container5.setFrameShape(QtWidgets.QFrame.Box)
        self.top_right_container5.setGeometry(QtCore.QRect(350,150,150,30))

        self.initializeScene5 = QtWidgets.QPushButton(self.top_right_container5)
        self.initializeScene5.setText('初始化场景')
        self.initializeScene5.setGeometry(400,300,300,100)

        return self.top_right_container5

    
    def creatSignaltable(self,  type):
        self.signalTable = QtWidgets.QTableWidget()
        self.signalTable.setObjectName("signalTable")
        # 设定初始的行数和列数
        if(type == 1):
            self.signalTable.setColumnCount(5)
            self.signalTable.setRowCount(40)
            self.signalTable.horizontalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
            self.signalTable.setHorizontalHeaderLabels(['中心频率', '带宽', '功率', 'Intercepts','Detections'])
            self.signalTable.horizontalHeader().setSectionResizeMode(4,QtWidgets.QHeaderView.Stretch)
        elif (type == 2):
            self.signalTable.setColumnCount(4)
            self.signalTable.setRowCount(40)
            self.signalTable.horizontalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
            self.signalTable.setHorizontalHeaderLabels(['时间','中心频率', '带宽', '调制方式'])
        else:
            self.signalTable.setColumnCount(7)
            self.signalTable.setRowCount(40)
            # self.signalTable.horizontalHeader().setSectionResizeMode(0,QtWidgets.QHeaderView.Stretch)
            self.signalTable.setHorizontalHeaderLabels(['时间','中心频率', '带宽', '调制方式','Duration','SNR', 'Confidence'])
            self.signalTable.horizontalHeader().setSectionResizeMode(4,QtWidgets.QHeaderView.Stretch)
            self.signalTable.horizontalHeader().setSectionResizeMode(5,QtWidgets.QHeaderView.Stretch)
            self.signalTable.horizontalHeader().setSectionResizeMode(6,QtWidgets.QHeaderView.Stretch)
            # self.signalTable.setColumnWidth(1,1000)  # 第三列设置的宽一点
        # 表头尺寸自动拉伸

        
        self.signalTable.horizontalHeader().setSectionResizeMode(1,QtWidgets.QHeaderView.Stretch)
        self.signalTable.horizontalHeader().setSectionResizeMode(2,QtWidgets.QHeaderView.Stretch)
        self.signalTable.horizontalHeader().setSectionResizeMode(3,QtWidgets.QHeaderView.Stretch)
        #self.signalTable.setColumnWidth(3,400)  # 第三列设置的宽一点
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

    