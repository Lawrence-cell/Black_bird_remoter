from math import fabs
from re import L, S, T
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from uitest import Ui_BlackBirdPanel
# from ui_control_panel import Ui_BlackBirdPanel
import random
#import pyqtgraph as pg
import numpy as np
from detectors_info import *
import socket
import struct
import time
import xlrd
from ejectWindow import *
from adjustThresholdWindow import *
import pickle
import load_data
import time
import os
import zmq
import detectors_info as detectors_info
from PyQt5.QtCore import QBuffer, QFileInfo, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QBrush, QPixmap, QStandardItemModel, QStandardItem, QColor, QFont

class WorkThread(QThread):
    triggger = pyqtSignal()
    def __init__(self, mainwindow, sceneIndex):
        super().__init__()
        self.mainwindow1 = mainwindow
        self.sceneIndex = sceneIndex
    def run(self):
        if self.sceneIndex == 1:
            while(True):
                if self.mainwindow1.flag == 1:
                    self.mainwindow1.global_signal_table = []
                    # print('*****************************************************************************')
                    # print(self.mainwindow1.lengthofTable2)
                    # print(self.mainwindow1.lengthofTable3)
                    #delat = require_data_from_N6820ES(self.mainwindow1.global_signal_table)#增量
                    require_data_from_N6820ES(self.mainwindow1.global_signal_table, self.mainwindow1.lengthofTable2)#增量
                    
                    # self.mainwindow1.global_signal_table[0].extend(delat[0])
                    # self.mainwindow1.global_signal_table[1].extend(delat[1])
                    # self.mainwindow1.global_signal_table[2].extend(delat[2])
                    #更新表格并绘图
                    self.mainwindow1.update_three_signal_table_and_curve()
            
def GetLocalIPByPrefix(prefix):
    r""" 多网卡情况下，根据前缀获取IP（Windows 下适用） """
    localIP = ''
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if ip.startswith(prefix):
            localIP = ip
    
    return localIP

def send_cmd(s,cmd_str):
    length = len(cmd_str)
    tag = 99  
    nLength = socket.htonl(length)
    nTag = socket.htonl(tag)
    pa = struct.pack('1L1L', nLength, nTag)
    s.send(pa+cmd_str)

def require_data_from_N6820ES(global_sig_var, lengthofSignaltable):

    HOST = GetLocalIPByPrefix('169.254')
    PORT = 7011
    try:
        socket_handler = socket.socket()
        print('connecting socket...')
        socket_handler.connect((HOST, PORT))
        socket_handler.recv(1024)
        print('connection done!!!')
    except Exception as e:
        print(type(e), e)         

    # my_folder_str = os.getcwd() 
    #  my_cmd = b'loadMissionSetup:' + my_folder_str.encode() +  'init_state.sta'
    # bytes_a + bytes_b
    # str -> bytes      my_str.encode()
    # step1 加载初始状态
    # command = b'loadMissionSetup: C:\\Users\\ying_T470s\\Desktop\\init_state.sta'
    # send_cmd(socket_handler,command)
    # time.sleep(0.1)
    this_project_path = os.getcwd() 
    
    if lengthofSignaltable == 0:
        command = b'clearSignalDatabase'
        send_cmd(socket_handler,command)
        time.sleep(0.1)
    
    command = b'saveEnergyHistory: ' + this_project_path.encode() + b'\\stateFile\\raw_Energy_history.his'
    send_cmd(socket_handler,command)


    command = b'saveSignalDatabase: '+ this_project_path.encode() + b'\\stateFile\\signalDatabase.his'
    send_cmd(socket_handler,command)


    command = b'clearSignalDatabase'
    send_cmd(socket_handler,command)
    time.sleep(0.1)
    # time.sleep(1)
    #随着时间累积 signaldatabase里的数据量越来越大 保存文件所需要的时间也在累积
    #所以可能需要根据运行时间增加sleep时间


    # command = b'clearEnergyHistory'
    # send_cmd(socket_handler,command)
    # time.sleep(15)

    #saveEnergyHistory: C:\\Users\\ying_T470s\\Desktop\\new_BlackBird\\stateFile\\raw_Energy_history.his

    


    socket_handler.close()

    #以上是从黑鸟中保存文件到本地
    #以下再从文件中读取数据到全局变量
    #tmp_sig = load_data.generate_signal_list()
    tmp_sig = load_data.readHisFile()
    #[all_energy, usd_showContent, modrec_showContent]
    #[[],[],[]]
    global_sig_var.extend(tmp_sig)
    
    

    # time_str = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime()) 
    # with open('history_data/'+ time_str + '.pkl','wb') as f:
    #     pickle.dump(tmp_sig,f)
    


def look_for_name(center_freq,bw):
    for i in range(len(detectors_bw_config)):
        min_bw = detectors_bw_config[i][0]* detectors_bw_config[i][1]
        max_bw = detectors_bw_config[i][0] * detectors_bw_config[i][2]
        if(  bw<max_bw  and bw>min_bw):
            for freq_range in detectors_bw_config[i][3:]:
                if( center_freq>freq_range[0] and center_freq<freq_range[1] ):
                    return detectors_name_lists[i],i

    return 'unknown',0




class BlackBirdPanel_MainWindow(QtWidgets.QMainWindow, Ui_BlackBirdPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.noise_value = -96
        self.setupUi(self)

        self.curve_color_lists = []
        self.every_curve_in_plot = []
        self.global_signal_table = [[],[],[]]
        self.timer = QTimer(self)

        self.curve_color_lists.append((46,139,87))
        self.curve_color_lists.append((0,0,128))
        self.curve_color_lists.append((255,193,37))
        self.curve_color_lists.append((255,106,106))

        self.worker = WorkThread(self, 1)
        self.worker.triggger.connect(self.workactionTrigger)
        self.flag = 0
        self.lengthofTable2 = 0
        self.lengthofTable3 = 0
        self.rgblist = []
        self.currentSceneIndex = 1
        for i in range(30):
            r = random.randint(0,254) 
            g = random.randint(0,253) 
            b = random.randint(0,254) 
            rgbItem = [r, g, b]
            self.rgblist.append(rgbItem)


        for i in range(27):
            tmpColor = tuple(np.random.choice(range(256),size=3))
            self.curve_color_lists.append(tmpColor)



        self.signalTable1.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单
        self.signalTable2.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单
        self.signalTable3.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单

        #
        # self.marker_arrow = pg.ArrowItem(pos=(1e9,-60),angle=-90,headLen=40)
        # self.marker_arrow.setZValue(1200)


        #**********************************************************signals and slots************************************************************
        #**********************************************************************************************************************************
        
        #self.signalTable1.itemClicked.connect(self.outSelect)#单击获取单元格中的内容

        #self.tw.tabBarClicked.connect(self.update_tab)
        # self.scene1_Btn.clicked.connect(lambda: self.switchScene(self.indexofScene1))
        # self.scene2Btn.clicked.connect(lambda: self.switchScene(self.indexofScene2))
        # self.scene3Btn.clicked.connect(lambda: self.switchScene(self.indexofScene3))
        # self.scene4Btn.clicked.connect(lambda: self.switchScene(self.indexofScene4))
        # self.scene5Btn.clicked.connect(lambda: self.switchScene(self.indexofScene5))
        self.cb.currentIndexChanged[int].connect(self.switchScene)
        # self.scene5Btn.clicked.connect(self.switchScene)

        self.start_button.clicked.connect(self.update_all)
        self.checkall_button.clicked.connect(self.check_all)
        self.uncheckall_button.clicked.connect(self.uncheck_all)
        self.checkall_button4.clicked.connect(self.check_all4)
        self.uncheckall_button4.clicked.connect(self.uncheck_all4)
        #self.decideDetectorBtn.clicked.connect(self.decideDetectors)
        self.scene1Btn.clicked.connect(self.loadscene1)
        self.bootBtn.clicked.connect(self.bootLaunch)#确定按钮 将detector以及扫频的改动应用
        self.autoRefresh.clicked.connect(self.startRefresh)
        self.handoffBtn.clicked.connect(self.handoffFunc)
        self.timer.timeout.connect(self.actionEveryTimeout)
        self.stopAuto.clicked.connect(self.stopTimer)
        self.save_Enviroment_Threshold.clicked.connect(self.saveEnvironmentFile)
        self.load_Environment_Threshold.clicked.connect(self.ejectaWindow)
        self.initializeScene2.clicked.connect(self.actionInitializeScene2)
        self.initializeScene3.clicked.connect(self.actionInitializeScene3)
        self.initializeScene5.clicked.connect(self.actionInitializeScene5)
        self.initializeScene4.clicked.connect(self.actionInitializeScene4)
        # self.initializeScene4.clicked.connect(self.loadscene1)

        self.adjustThreshold.clicked.connect(self.actionAdjustThreshold)
        
        
        for i in self.checkbox_lists:
            i.stateChanged.connect(self.findMinandMax)

        self.showMaximized()

    def actionInitializeScene4(self):
        self.signalTable1.clearContents()
        self.signalTable2.clearContents()
        self.signalTable3.clearContents()
        self.lengthofTable2 = 0 
        self.lengthofTable3 = 0

        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     

        this_project_path = os.getcwd() 
        
        command =  b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\init_state_scene4.sta'
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        self.startFrequency.setText('1090')
        self.stopFrequency.setText('18')
        # self.worker.terminate()
        # self.worker = WorkThread(self, 1)
        socket_handler.close()    

    def actionInitializeScene5(self):
        self.signalTable1.clearContents()
        self.signalTable2.clearContents()
        self.signalTable3.clearContents()
        self.lengthofTable2 = 0 
        self.lengthofTable3 = 0

        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     

        this_project_path = os.getcwd() 
        
        command =  b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\init_state_scene5.sta'
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        self.startFrequency.setText('1090')
        self.stopFrequency.setText('18')
        # self.worker.terminate()
        # self.worker = WorkThread(self, 1)
        socket_handler.close()    




    def actionThdApply(self):
        thd = self.adjustThd_ejectWindow.thdValue.toPlainText()
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e) 
        if self.adjustThd_ejectWindow.autoMode.isChecked() == True:
            command =  b'thresholdMargin: ' + thd.encode()
        else:
            command =  b'thresholdOffset: ' + thd.encode()
        
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        socket_handler.close()    
        
        
        self.adjustThd_ejectWindow.close()

    def actionAdjustThreshold(self):
        self.adjustThd_ejectWindow = adjustThd_ejectWindow()
        self.adjustThd_ejectWindow.autoMode.stateChanged.connect(self.actionAutoMode)
        self.adjustThd_ejectWindow.levelMode.stateChanged.connect(self.actionLevelMode)
        self.adjustThd_ejectWindow.thdApplyBtn.clicked.connect(self.actionThdApply)     
        self.adjustThd_ejectWindow.show()

    def actionAutoMode(self, state):
        if state == Qt.Checked:
            self.adjustThd_ejectWindow.levelMode.setChecked(False)
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     
        command =  b'thresholdMode: Auto' 
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        socket_handler.close()    
    
    def actionLevelMode(self, state):
        if state == Qt.Checked:
            self.adjustThd_ejectWindow.autoMode.setChecked(False)
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     
        command =  b'thresholdMode: Level' 
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        socket_handler.close()    

    def actionInitializeScene3(self):
        self.signalTable1.clearContents()
        self.signalTable2.clearContents()
        self.signalTable3.clearContents()
        self.lengthofTable2 = 0 
        self.lengthofTable3 = 0

        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     

        this_project_path = os.getcwd() 
        
        command =  b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\init_state_scene3.sta'
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        self.startFrequency.setText('470')
        self.stopFrequency.setText('510')
        # self.worker.terminate()
        # self.worker = WorkThread(self, 1)
        socket_handler.close()    


    def actionInitializeScene2(self):
        self.signalTable1.clearContents()
        self.signalTable2.clearContents()
        self.signalTable3.clearContents()
        self.lengthofTable2 = 0 
        self.lengthofTable3 = 0

        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     

        this_project_path = os.getcwd() 
        
        command =  b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\init_state_scene2.sta'
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        self.startFrequency.setText('1805')
        self.stopFrequency.setText('1850')
        # self.worker.terminate()
        # self.worker = WorkThread(self, 1)
        socket_handler.close()    

    def ejectaWindow(self):
        self.ejectWindow = test_taowa()
        file_list = []
        for f in os.listdir('environmentHistory'):
            file_list.append(f)

        self.ejectWindow.signalTable.setRowCount(len(file_list)+10)

        print(file_list)
        self.ejectWindow.signalTable.clearContents()

        for i in range(len(file_list)):
            item = QTableWidgetItem(file_list[i])
            self.ejectWindow.signalTable.setItem(i, 0, item) 

        self.ejectWindow.historyRecord.itemDoubleClicked.connect(self.action_DoubleClicked) 
        self.ejectWindow.show()


    def saveEnvironmentFile(self):
        # thresholdMode: Environment
        # environmentThresholdMode: ManualAcquire
        # ...sleep 5~10s...
        # saveBinaryThreshold: userthd.thd
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)         

        this_project_path = os.getcwd() 
        
        command = b'thresholdMode: Environment'
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        
        command = b'environmentThresholdMode: ManualAcquire'
        send_cmd(socket_handler,command)
        time.sleep(5)


        timeCurrent = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        list = timeCurrent.split(' ')
        hourminsec = list[1].split(':')
        filename = list[0] + '-'+ hourminsec[0] + '-' + hourminsec[1] + '-' + hourminsec[2] + '.thd'

        command = b'saveBinaryThreshold: ' + this_project_path.encode() + b'\\environmentHistory\\'  + filename.encode()
        send_cmd(socket_handler,command)
        socket_handler.close()

    def switchScene(self, index):
        self.stackedWidget.setCurrentIndex(index)
        if index == self.indexofScene1 :
            self.tw.setTabText(0, '所有信号')
            self.tw.setTabText(1, '备案信号')
            self.tw.setTabText(2, '未知信号')
            self.tw.setTabEnabled(1, True)
            self.tw.setTabEnabled(2, True)
            self.currentSceneIndex = 1
            self.startFreLabel.setText('扫描开始频率(MHz)')
            self.stopFreLabel.setText('扫描结束频率(MHz)')
            
            

        if index == self.indexofScene2 :
            self.tw.setTabText(0, '能量历史')
            self.tw.setTabText(1, '        ')
            self.tw.setTabText(2, '信号历史')
            self.tw.setTabEnabled(1, False)
            self.tw.setTabEnabled(2, True)
            self.currentSceneIndex = 2
            self.startFreLabel.setText('扫描开始频率(MHz)')
            self.stopFreLabel.setText('扫描结束频率(MHz)')
            
            

        if index == self.indexofScene3 :
            self.tw.setTabText(0, '能量历史')
            self.tw.setTabText(1, '       ')
            self.tw.setTabText(2, '信号历史')
            self.tw.setTabEnabled(1, False)
            self.tw.setTabEnabled(2, True)
            self.currentSceneIndex = 3
            self.startFreLabel.setText('扫描开始频率(MHz)')
            self.stopFreLabel.setText('扫描结束频率(MHz)')
            
            
        if index == self.indexofScene4 :
            self.tw.setTabText(0, '能量历史')
            self.tw.setTabText(1, '异常信号')
            self.tw.setTabText(2, '')
            self.tw.setTabEnabled(2, False)
            self.tw.setTabEnabled(1, True)
            self.startFreLabel.setText('中心频点(MHz)')
            self.stopFreLabel.setText('带宽(MHz)')
            self.currentSceneIndex = 4

        if index == self.indexofScene5:
            self.currentSceneIndex = 5
            self.startFreLabel.setText('中心频点(MHz)')
            self.stopFreLabel.setText('带宽(MHz)')

    


    def findMinandMax(self):
        min = 7e9
        max = 0
        detecorsNames = []
        for index ,i in enumerate(self.checkbox_lists):
            if i.isChecked() == True :
                detecorsNames.append(i.text())
                if detectors_info.detectors_bw_config[index][3][0] < min :
                    min = detectors_info.detectors_bw_config[index][3][0]
                if detectors_info.detectors_bw_config[index][-1][1] > max :
                    max = detectors_info.detectors_bw_config[index][-1][1]
        self.startFrequency.setText(str(min/1e6))
        self.stopFrequency.setText(str(max/1e6))

    def workactionTrigger(self):
        print('\nreceive sig!!')
        self.worker.start()


    def actionEveryTimeout(self):
        self.update_all()

    def stopTimer(self):
        self.flag = 0
        # self.timer.stop()
        #结束按钮不可点击，开始按钮可以点击
        self.autoRefresh.setEnabled(True)
        self.stopAuto.setEnabled(False)

    def handoffFunc(self):
        self.global_signal_table = []
        valid_index = []
        # 检查checkbox的状态
        for cnt in range(30):
            if(self.checkbox_lists[cnt].isChecked()):
                valid_index.append(cnt)

        require_data_from_N6820ES(self.global_signal_table, self.lengthofTable3)
        
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        #socket.bind("tcp://10.128.223.175:8000")
        socket.bind("tcp://192.168.10.1:8000")


        print(self.global_signal_table)
        #data = input("input your data:")
        data = str(self.global_signal_table)
        time.sleep(0.5)

        print(data)
        for i in range(5):
            socket.send_string(data)
            time.sleep(0.1)
        #socket.close()


    def startRefresh(self):
        self.flag = 1
        self.worker.start()
        # self.timer.start(3500)
        print("sadsadasdasdasdasdas")
        self.autoRefresh.setEnabled(False)
        self.stopAuto.setEnabled(True)


    def action_DoubleClicked(self, item):
        #thresholdFilename: userthd.thd
        # thresholdMode: File
        # 【thresholdOffset: integer 
        # -50 ≤ integer ≤ 50】
        filename = item.text()

        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)     

        this_project_path = os.getcwd() 
        
        command = b'thresholdFilename: ' + this_project_path.encode() + b'\\environmentHistory\\' + filename.encode()
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        command = b'thresholdMode: File'
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        command = b'thresholdOffset: -5 '
        send_cmd(socket_handler,command)
        time.sleep(0.1)

        socket_handler.close()  
    
        # self.global_signal_table.clear()
        self.ejectWindow.close()
        

    def generateMenu(self, pos):
        menu = QtWidgets.QMenu()
        signalTable =  QtWidgets.QTableWidget()
        currentTabIndex = self.tw.currentIndex()
        if currentTabIndex == 0 :
            signalTable = self.signalTable1
        elif currentTabIndex == 1 :
            signalTable = self.signalTable2
        elif currentTabIndex == 2 :
            signalTable = self.signalTable3

        item1 = menu.addAction(u"识别调制方式")
        action = menu.exec_(signalTable.mapToGlobal(pos))

        print('test')
        print(pos)
        print(signalTable.mapToGlobal(pos))


        if action == item1:
            self.do_AMC_in_this_row()
        else:
            return

        
    def check_all(self):
        for i in self.checkbox_lists:
            i.setChecked(True)
        
    def uncheck_all(self):
        for i in self.checkbox_lists:
            i.setChecked(False)   
        self.startFrequency.setText('0.0')
        self.stopFrequency.setText('0.0')


    def check_all4(self):
        for i in self.checkbox_lists4:
            i.setChecked(True)
        
    def uncheck_all4(self):
        for i in self.checkbox_lists4:
            i.setChecked(False)   

    # 更新三张表的内容
    def update_three_signal_table_and_curve(self):

        signal_lists = self.global_signal_table
        # 这里规定signal_lists第一个元素内容是信号总表，第二个元素是备案信号表，第三个元素是未知信号表
        for table_cnt in range(3):
            
            if(table_cnt==0):
                self.signalTable1.clearContents() # 清空第一张表
                current_tab = self.signalTable1
                show_content = signal_lists[0]

                for row,i in enumerate(show_content):
                    
                #设置中心频率
                    item = QTableWidgetItem("{:0.2f}  [MHz]".format( i[0]/1e6 ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(row, 0, item)
                   
                    #设置带宽
                    if(i[1]<1e6):
                        item = QTableWidgetItem("{:0.1f}  [kHz]".format( i[1]/1e3 ))
                    else:
                        item = QTableWidgetItem("{:0.1f}  [MHz]".format( i[1]/1e6 ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(row, 1, item)        

                    #设置接收功率
                    item = QTableWidgetItem("{:0.1f}  [dBm]".format( i[2] ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(row, 2, item)    

                    #设置备案信息
                    item = QTableWidgetItem("{}  ".format(int(i[3])))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(row, 3, item)    
                
                    item = QTableWidgetItem("{}  ".format( int(i[4]) ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(row, 4, item) 
                    
                    
                current_tab.setRowCount(len(show_content) + 10)
        
            elif(table_cnt==1):
                #self.signalTable2.clearContents() # 清空第二张表
                current_tab = self.signalTable2
                show_content = signal_lists[1]
                current_tab.setRowCount(self.lengthofTable2 + len(show_content))
                for row,i in enumerate(show_content):
                    # if(len(i[0])==0):
                    #     print(show_content)
                    #     raise 
                    
                    strlist = i[3].split(' ')
                    strlist = strlist[0].split('_')
                    colorNum = int(strlist[0])
                    #设置时间
                    item = QTableWidgetItem(i[0] )
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable2 + row, 0, item)
                    item.setForeground(QBrush(QColor(10 * colorNum  , 4 * colorNum , 8 * colorNum)))
                    item.setForeground(QBrush(QColor(self.rgblist[colorNum][0], self.rgblist[colorNum][1], self.rgblist[colorNum][2])))

                    #设置频率
                    item = QTableWidgetItem("{:0.1f}  [MHz]".format( float(i[1])/1e6 ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable2 + row, 1, item)
                    item.setForeground(QBrush(QColor(10 * colorNum , 4 * colorNum , 8 * colorNum)))
                    item.setForeground(QBrush(QColor(self.rgblist[colorNum][0], self.rgblist[colorNum][1], self.rgblist[colorNum][2])))            

                    #设置带宽
                    if(float(i[2])<1e6):
                        item = QTableWidgetItem("{:0.1f}  [kHz]".format( float(i[2])/1e3 ))
                    else:
                        item = QTableWidgetItem("{:0.1f}  [MHz]".format( float(i[2])/1e6 ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    item.setForeground(QBrush(QColor(10 * colorNum , 4 * colorNum , 8 * colorNum)))
                    item.setForeground(QBrush(QColor(self.rgblist[colorNum][0], self.rgblist[colorNum][1], self.rgblist[colorNum][2])))
                    current_tab.setItem(self.lengthofTable2 + row, 2, item)            

                    #设置调制方式
                    item = QTableWidgetItem(i[3])
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    item.setForeground(QBrush(QColor(10 * colorNum , 4 * colorNum , 8 * colorNum)))
                    item.setForeground(QBrush(QColor(self.rgblist[colorNum][0], self.rgblist[colorNum][1], self.rgblist[colorNum][2])))
                    current_tab.setItem(self.lengthofTable2 + row, 3, item)               
                self.lengthofTable2 = self.lengthofTable2 + len(show_content)
                # print('this loop rows:')
                # print(self.lengthofTable2) 
                # print(show_content[-10:])
                # print(len(show_content))
                # print('\n')
                    # 每次刷新在原有基础上附加增量
                

            else:
                # self.signalTable3.clearContents()  
                current_tab = self.signalTable3
                show_content = signal_lists[2]
                current_tab.setRowCount(self.lengthofTable3 + len(show_content))
                for row,i in enumerate(show_content):
                    flag = 1
                    if i[5] == '--':
                        flag = 0
                    #设置时间
                    
                    item = QTableWidgetItem(i[0] )
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 0, item)
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))

                    #设置频率
                    
                    item = QTableWidgetItem("{:0.1f}  [MHz]".format(float(i[1]) /1e6 ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 1, item) 
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))           

                    #设置带宽
                    if(float(i[2])<1e6):
                        item = QTableWidgetItem("{:0.1f}  [kHz]".format( float(i[2])/1e3 ))
                    else:
                        item = QTableWidgetItem("{:0.1f}  [MHz]".format( float(i[2])/1e6 ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 2, item)      
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))      

                    #设置调制方式
                    item = QTableWidgetItem(i[3])
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 3, item)    
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))

                    #设置duration
                    item = QTableWidgetItem("{:0.1f}  [Sec]".format( float(i[4]) ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 4, item)
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))
                    
                    #设置SNR
                    if i[5] == '--':
                        item = QTableWidgetItem(i[5])
                    else:
                        item = QTableWidgetItem("{:0.1f}  [dB]".format( float(i[5]) ))
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 5, item)
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))

                    #设置Confidence
                    item = QTableWidgetItem(i[6])
                    item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                    current_tab.setItem(self.lengthofTable3 + row, 6, item)
                    if flag == 1 :
                        item.setBackground(QBrush(QColor(0,220,220)))
                self.lengthofTable3 = self.lengthofTable3 + len(show_content)
                # current_tab.setRowCount(self.lengthofTable3 + 30)

    def update_all(self):
        #self.global_signal_table = []
        valid_index = []
        # 检查checkbox的状态
        for cnt in range(30):
            if(self.checkbox_lists[cnt].isChecked()):
                valid_index.append(cnt)

        self.global_signal_table = []
        require_data_from_N6820ES(self.global_signal_table, self.lengthofTable3)#增量
        # self.global_signal_table[0].extend(delat[0])
        # self.global_signal_table[1].extend(delat[1])
        # self.global_signal_table[2].extend(delat[2])
        #更新表格并绘图
        self.update_three_signal_table_and_curve()
        print('*****************************************************************************')
        print(self.lengthofTable2)
        print(self.lengthofTable3)
        


    def updateThreeSignalTable(self):
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)       
        this_project_path = os.getcwd() 
        command = b'saveEnergyHistory: ' + this_project_path.encode() + b'\\stateFile\\raw_Energy_history.his'
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        socket_handler.close()
        

    def loadscene1(self):
        self.signalTable1.clearContents()
        self.signalTable2.clearContents()
        self.signalTable3.clearContents()
        self.lengthofTable2 = 0 
        self.lengthofTable3 = 0

        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)         

        this_project_path = os.getcwd() 
        command = b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\init_state_scene1.sta'
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        self.checkbox_lists[0].setChecked(True)
        self.startFrequency.setText('88')
        self.stopFrequency.setText('108')
        socket_handler.close()

    def bootLaunch_scene2(self):
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)         

  
        startF = self.startFrequency_scene2.toPlainText()
        stopF = self.stopFrequency_scene2.toPlainText()
 
        command = b'startFrequency: ' + startF.encode() + b'MHz'
        send_cmd(socket_handler,command)
        # time.sleep(0.1)
        
        send_cmd(socket_handler,command)
        
    
        command = b'stopFrequency: ' + stopF.toPlainText().encode() + b'MHz'
        send_cmd(socket_handler,command)
        # time.sleep(0.1)
        
        socket_handler.close()

    def bootLaunch(self):
    
        
        HOST = GetLocalIPByPrefix('169.254')
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)         


        startF = float(self.startFrequency.toPlainText())
        stopF = float(self.stopFrequency.toPlainText())
        if self.currentSceneIndex == 5 or 4:
            startF = startF - stopF/2.0
            stopF= startF + stopF
            startF = str(startF)
            stopF = str(stopF)
        if float(startF) < float(stopF):
            command = b'startFrequency: ' + startF.encode() + b'MHz'
            send_cmd(socket_handler,command)
            # time.sleep(0.1)
            
            send_cmd(socket_handler,command)
            
        
            command = b'stopFrequency: ' + stopF.encode() + b'MHz'
            send_cmd(socket_handler,command)
            # time.sleep(0.1)
        else:
            self.startFrequency.setText('88')
            self.stopFrequency.setText('108')

            command = b'startFrequency: ' + b'88' + b'MHz'
            send_cmd(socket_handler,command)
            # time.sleep(0.1)
            
            send_cmd(socket_handler,command)
            
        
            command = b'stopFrequency: ' + b'108' + b'MHz'
            send_cmd(socket_handler,command)
            # time.sleep(0.1)
        detecorsNames = []
        
        ###以下发送usd选择模板command
        command = b'usd.global: USD.GLOBAL.0,1,-150,0,3600,0' 
        send_cmd(socket_handler,command)
        time.sleep(0.1)
       
        for index ,i in enumerate(self.checkbox_lists):
            if i.isChecked() == True :
                detecorsNames.append(i.text())

        for i in detecorsNames:
            #按照选中detector依次发送command到黑鸟
            command = b'usd.signal1: USD.SIGNAL.0,'  + i.encode() + b',bupt,1,6,0,0,0,4,16000,0,-180,1,0,2,USD_<T%y_%m_%d_%H_%M_%S><E>,3,600,6,5,-90,5,5'
            send_cmd(socket_handler,command)
            time.sleep(0.1)
        
        if self.currentSceneIndex == 4 :
            #11111111111111111
            #11111111111011111
            valid_list = []
            for i in range(29):
               valid_list.append('1')
            for index,i in enumerate (self.checkbox_lists4):
                if i.isChecked() == True:
                    valid_list[index] = '0'
            str1=''.join(valid_list) 
            str1 = str(int(str1, 2))
            print(str1)
        #alarm3.signalIdSetup: A.00.00 1 536870911 0 1 10 10000 0 1 100 10000 0 1 6 6 0 1 90 100
            command = b'alarm3.signalIdSetup: A.00.00 1 ' + str1.encode() + b' 0 1 10 10000 0 1 100 10000 0 1 6 6 0 1 90 100'
            send_cmd(socket_handler,command)
            time.sleep(0.1)   
        
        socket_handler.close()

        

               
if __name__ == "__main__":   
   
    np.random.seed(1)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("黑鸟监测")
    root = QFileInfo(__file__).absolutePath()
    app.setWindowIcon(QIcon(root+'/stateFile/Freq.ico'))
    window = BlackBirdPanel_MainWindow()
    sys.exit(app.exec_())





