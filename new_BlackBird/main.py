import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
from ui_control_panel import Ui_BlackBirdPanel
import random
import pyqtgraph as pg
import numpy as np
from detectors_info import *
import socket
import struct
import time
import xlrd
from ejectWindow import *
import pickle
import load_data
import time
import os


def calc_spectrum_curve(freq_range,noise,avg_power):
    out = []
    factor = 0.1  #决定了曲线的陡峭程度
    bin_interval = 500
    bin_num = int((freq_range[1] - freq_range[0])//bin_interval)
    up_and_down_num = int(bin_num * factor)
    edge = list((np.cos(np.linspace(0,2*np.pi,up_and_down_num*2))+1)/2)
    out.extend(edge[up_and_down_num:])
    out.extend([1]*bin_num)
    out.extend(edge[0:up_and_down_num])
    gap = avg_power-noise
    y_axis = [i*gap+noise for i in out]

    x_axis = list(np.linspace(freq_range[0]-bin_interval*up_and_down_num,
                                freq_range[1]+bin_interval*up_and_down_num,len(out)))
    return x_axis,y_axis




def send_cmd(s,cmd_str):
    length = len(cmd_str)
    tag = 99  
    nLength = socket.htonl(length)
    nTag = socket.htonl(tag)
    pa = struct.pack('1L1L', nLength, nTag)
    s.send(pa+cmd_str)

def start_AMC(cf,bw):
    
    HOST = '169.254.40.236'
    PORT = 7011
    try:
        socket_handler = socket.socket()
        print('connecting socket...')
        socket_handler.connect((HOST, PORT))
        socket_handler.recv(1024)
        print('connection done!!!')
    except Exception as e:
        print(type(e), e)     


    bytes_cf = str.encode(str(int(cf)))
    bytes_bw = str.encode(str(int(bw)))

    # # 先暂停扫频，在做完AMC之后再恢复
    # cmd_stop = b'stop'
    # send_cmd(socket_handler,cmd_stop)
    # time.sleep(0.1)

    
    cmd_set_cf = b'traceB.markerToFrequency: ' + bytes_cf + b' Hz'
    cmd_set_bw = b'traceB.markerBandwidth: ' + bytes_bw
    send_cmd(socket_handler,cmd_set_cf)
    send_cmd(socket_handler,cmd_set_bw)

    command1 = b'mrGeometry: 0 0 498 151 896 541'
    send_cmd(socket_handler,command1)
    # command2 = b'modRec1.geometry: 0 197 636 73 325 305 302'
    # send_cmd(socket_handler,command2)
    command3 = b'traceB.doMarkerModRec'
    send_cmd(socket_handler,command3)


    # TODO 能否不使用软件中的USD功能？？？
    # TODO 1、通过某种方式，使得AMC执行完成之后才重新启动扫频，可以使用窗口检测，可以设定一个略大于AMC消耗时间的值
    # TODO 2、保存截图
    # # TODO 3、识别
    # time.sleep(30)
    # send_cmd(socket_handler,b'start')

    socket_handler.close()


    # 


def require_data_from_N6820ES(global_sig_var):

    HOST = '169.254.40.236'
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
    command = b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\init_state.sta'
    send_cmd(socket_handler,command)
    time.sleep(0.1)
    
    # step2 导出auto模式下的energy history
    command = b'thresholdMode: Auto'
    send_cmd(socket_handler,command)
    time.sleep(0.1)

    command = b'clearEnergyHistory'
    send_cmd(socket_handler,command)
    time.sleep(7)

    command = b'saveEnergyHistory: ' + this_project_path.encode() + b'\\stateFile\\raw_Energy_history.his'
    #command = b'saveEnergyHistory: C:\\Users\\ying_T470s\\Desktop\\raw_Energy_history.his'
    send_cmd(socket_handler,command)
    time.sleep(0.1)

    command = b'saveAsciiThreshold:' + this_project_path.encode() + b'\\stateFile\\raw_Threshold.his'
    #command = b'saveAsciiThreshold: C:\\Users\\ying_T470s\\Desktop\\raw_Threshold.his'
    send_cmd(socket_handler,command)
    time.sleep(0.1)
    
    command = b'preFiltersEnabled: True'
    send_cmd(socket_handler,command)
    time.sleep(0.1)

    command = b'clearEnergyHistory'
    send_cmd(socket_handler,command)
    time.sleep(7)

    command = b'saveEnergyHistory: ' + this_project_path.encode() + b'\\stateFile\\auto_USD_Energy_history.his'
    #command = b'saveEnergyHistory: C:\\Users\\ying_T470s\\Desktop\\auto_USD_Energy_history.his'
    send_cmd(socket_handler,command)
    time.sleep(0.1)

    command = b'thresholdMode: Level'
    send_cmd(socket_handler,command)
    time.sleep(0.1)

    command = b'thresholdLevel: -96'
    send_cmd(socket_handler,command)
    time.sleep(7)

    command = b'saveEnergyHistory: ' + this_project_path.encode() + b'\\stateFile\\level_USD_Energy_history.his'
    #command = b'saveEnergyHistory: C:\\Users\\ying_T470s\\Desktop\\level_USD_Energy_history.his'
    send_cmd(socket_handler,command)
    time.sleep(0.1)

    socket_handler.close()

    #以上是从黑鸟中保存文件到本地
    #以下再从文件中读取数据到全局变量
    tmp_sig = load_data.generate_signal_list()
    global_sig_var.extend(tmp_sig)

    time_str = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime()) 
    with open('history_data/'+ time_str + '.pkl','wb') as f:
        pickle.dump(tmp_sig,f)
    


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
        self.global_signal_table = []

        self.curve_color_lists.append((46,139,87))
        self.curve_color_lists.append((0,0,128))
        self.curve_color_lists.append((255,193,37))
        self.curve_color_lists.append((255,106,106))



        for i in range(27):
            tmpColor = tuple(np.random.choice(range(256),size=3))
            self.curve_color_lists.append(tmpColor)



        self.signalTable1.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单
        self.signalTable2.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单
        self.signalTable3.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单


        self.marker_arrow = pg.ArrowItem(pos=(1e9,-60),angle=-90,headLen=40)
        self.marker_arrow.setZValue(1200)
        

        self.signalTable1.cellClicked.connect(self.show_marker_in_this_signal)
        self.signalTable2.cellClicked.connect(self.show_marker_in_this_signal)
        self.signalTable3.cellClicked.connect(self.show_marker_in_this_signal)


        #self.signalTable1.itemClicked.connect(self.outSelect)#单击获取单元格中的内容
   
        self.tw.tabBarClicked.connect(self.update_tab)
        self.start_button.clicked.connect(self.update_all)
        self.checkall_button.clicked.connect(self.check_all)
        self.uncheckall_button.clicked.connect(self.uncheck_all)
        self.decideDetectorBtn.clicked.connect(self.decideDetectors)
        self.scene1Btn.clicked.connect(self.loadscene1)
        self.bootBtn.clicked.connect(self.bootLaunch)
        #self.checkall_button

        self.showMaximized()



    def action_DoubleClicked(self, item):
        path = 'history_data/'
        path = path + item.text()
        with open(path, 'rb') as f:
            cont = pickle.load(f)
        self.global_signal_table.clear()
        self.ejectWindow.close()
        
        self.global_signal_table.extend(cont)
        self.update_three_signal_table_and_curve()
        
        # print(item.text())

    def upload_HistoryData(self, list):
      
        for i in range(len(list)):
            
            item = QTableWidgetItem(str(i))
            self.ejectWindow.signalTable.setItem(i, 0, item)
            #中心频率
            item = QTableWidgetItem("{:0.2f}".format( float(list[1])))
            self.ejectWindow.signalTable.setItem(i, 1, item)
            #带宽
            item = QTableWidgetItem("{:0.1f}".format( float(list[2])))
            self.ejectWindow.signalTable.setItem(i, 2, item)
    



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

    def do_AMC_in_this_row(self):

        if(self.tw.currentIndex()==0):
            row_cnt = self.signalTable1.currentRow()
        elif(self.tw.currentIndex()==1):
            row_cnt = self.signalTable2.currentRow()
        else:
            row_cnt = self.signalTable3.currentRow()

        print(row_cnt)

        sig = self.global_signal_table[self.tw.currentIndex()][row_cnt]
        start_AMC(sig[0],sig[1])


        # for item in signalTable.selectedItems():
        #     current_row = item.row()
        #     if current_row in row_list:
        #         continue
        #     else:
        #         row_list.append(current_row)
        # tmp_cf = 
        # print(signalTable.item(row_list[0],0).text())
        # print(signalTable.item(row_list[0],1).text())

        
    def check_all(self):
        for i in self.checkbox_lists:
            i.setChecked(True)
        
    def uncheck_all(self):
        for i in self.checkbox_lists:
            i.setChecked(False)   


    # 更新三张表的内容
    def update_three_signal_table_and_curve(self):

        signal_lists = self.global_signal_table

        # 先清空三张表
        self.signalTable1.clearContents()
        self.signalTable2.clearContents()
        self.signalTable3.clearContents()


        # 这里规定signal_lists第一个元素内容是信号总表，第二个元素是备案信号表，第三个元素是未知信号表
        for table_cnt in range(3):
            if(table_cnt==0):
                current_tab = self.signalTable1
                show_content = signal_lists[0]
            elif(table_cnt==1):
                current_tab = self.signalTable2
                show_content = signal_lists[1]
            else:
                current_tab = self.signalTable3
                show_content = signal_lists[2]

            current_tab.setRowCount(len(show_content)+30)

            # 依次填写每一张表
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
                item = QTableWidgetItem(i[3])
                item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)  #内容居中
                current_tab.setItem(row, 3, item)    


        self.update_curve(self.tw.currentIndex())


    ##################### 根据当前观察的表格内容，把信号曲线绘制上去 #######################3#####

    # 绘制当前tab窗口中，表格里的信号曲线
    def update_curve(self,tab_id):
        signal_lists = self.global_signal_table
        show_curve_sig = signal_lists[tab_id] # 0对应表一，1对应表二，2对应表三
        self.bottom_right_plot.clear()

        self.bottom_right_plot.addItem(self.marker_arrow )
        self.marker_arrow.setVisible(False)


        # 添加一条白色的噪声标识线
        noise_baseline = self.bottom_right_plot.plot(pen=pg.mkColor('w'))
        noise_value = self.noise_value
        noise_baseline.setData(np.linspace(20e6,6e9,100), [noise_value]*100)   # 这里应该根据监测软件使用的噪声电平值来设定

        # 存储不同信号曲线的坐标序列
        # 三维列表，第一维表示是什么类型的信号，比如FM\GSM\LTE\未知信号等
        # 第二维表示选择X轴还是Y轴
        # 第三维表示此轴上的数据点序列
        self.curve_plot_data_lists = [[[],[]] for i in range(30)]

        for cnt, sig in enumerate(show_curve_sig):
            min_f = float(sig[0]) - float(sig[1])/2
            max_f = float(sig[0]) + float(sig[1])/2
            freq_range = (min_f,max_f)   
            x,y = calc_spectrum_curve(freq_range,self.noise_value,sig[2]) 

            if(sig[3].find('FM')!=-1):
                self.curve_plot_data_lists[0][0].extend(x)
                self.curve_plot_data_lists[0][1].extend(y)
            elif(sig[3].find('GSM')!=-1):
                self.curve_plot_data_lists[1][0].extend(x)
                self.curve_plot_data_lists[1][1].extend(y)
            elif(sig[3].find('LTE')!=-1):
                self.curve_plot_data_lists[2][0].extend(x)
                self.curve_plot_data_lists[2][1].extend(y)                        
            else:
                self.curve_plot_data_lists[3][0].extend(x)
                self.curve_plot_data_lists[3][1].extend(y)


        lengend_name_list=['FM','GSM','LTE','未知信号']

        self.every_curve_in_plot.clear()  # 清空这个全局列表


        ## 绘图        
        for i in range(30):
            if(  len(self.curve_plot_data_lists[i][0])!=0  ):
                
                one_curve = self.bottom_right_plot.plot(pen=pg.mkColor(self.curve_color_lists[i]),name=lengend_name_list[i])
                one_curve.setZValue(10)
                one_curve.setData(self.curve_plot_data_lists[i][0],  self.curve_plot_data_lists[i][1])
                self.every_curve_in_plot.append(one_curve)


    def show_marker_in_this_signal(self,row,column):
        if(self.tw.currentIndex()>len(self.global_signal_table)):
            pass
        else:
            sig = self.global_signal_table[self.tw.currentIndex()][row]
            self.marker_arrow.setPos(sig[0],sig[2])
            self.marker_arrow.setVisible(True)



    def update_tab(self,tab_index):
        self.update_curve(tab_index)


    def update_all(self):
        self.global_signal_table = []
        valid_index = []
        # 检查checkbox的状态
        for cnt in range(30):
            if(self.checkbox_lists[cnt].isChecked()):
                valid_index.append(cnt)

        require_data_from_N6820ES(self.global_signal_table)

        #更新表格并绘图
        self.update_three_signal_table_and_curve()
    

    def updateThreeSignalTable(self):
        HOST = '169.254.40.236'
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

    def loadscene1(self):
        HOST = '169.254.40.236'
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
        command = b'loadMissionSetup:' + this_project_path.encode() + b'\\stateFile\\tfytt.sta'
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        self.startFrequency.setText('88')
        self.stopFrequency.setText('108')
        socket_handler.close()
        
    def bootLaunch(self):
    
        
        HOST = '169.254.40.236'
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
        command = b'startFrequency: ' + self.startFrequency.toPlainText().encode() + b'MHz'
        send_cmd(socket_handler,command)
        time.sleep(7)
        command = b'stopFrequency: ' + self.stopFrequency.toPlainText().encode() + b'MHz'
        send_cmd(socket_handler,command)
        time.sleep(7)
        self.checkbox_lists[0].setChecked(True)

        
        time.sleep(0.1)
        socket_handler.close()

    
    def decideDetectors(self):
        HOST = '169.254.40.236'
        PORT = 7011
        try:
            socket_handler = socket.socket()
            print('connecting socket...')
            socket_handler.connect((HOST, PORT))
            socket_handler.recv(1024)
            print('connection done!!!')
        except Exception as e:
            print(type(e), e)         

        #发送命令：清空USD选中模板
        detecorsNames = []
        command = b'usd.global: USD.GLOBAL.0,0,-150,0,3600,0' 
        send_cmd(socket_handler,command)
        time.sleep(0.1)
        for i in self.checkbox_lists:
            if i.isChecked() == True :
                detecorsNames.append(i.text())
        for i in detecorsNames:
            #按照选中detector依次发送command到黑鸟
            command = b'usd.signal1: USD.SIGNAL.0,'  + i.encode() + b',bupt,1,6,0,0,0,4,16000,0,-180,1,0,2,USD_<T%y_%m_%d_%H_%M_%S><E>,3,600,6,5,-90,5,5'
            send_cmd(socket_handler,command)
            time.sleep(0.1)
        socket_handler.close()
               
if __name__ == "__main__":   
   
    np.random.seed(1)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("黑鸟监测")
    window = BlackBirdPanel_MainWindow()
    sys.exit(app.exec_())





