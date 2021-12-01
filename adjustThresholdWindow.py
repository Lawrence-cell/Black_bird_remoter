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
        self.horizontalLayout = QtWidgets.QGridLayout(self.centralwidget) 
        self.autoMode = QtWidgets.QCheckBox('auto 门限模式')
        self.levelMode = QtWidgets.QCheckBox('level 门限模式')

 
        self.topContainer = QtWidgets.QFrame()
        self.topContainer.setFrameShape(QtWidgets.QFrame.Box)
        self.topLayout = QtWidgets.QGridLayout(self.topContainer)

        self.topLayout.addWidget(self.autoMode,0,0)
        self.topLayout.addWidget(self.levelMode,0,1)



        self.bottomContainer = QtWidgets.QFrame()
        self.bottomContainer.setFrameShape(QtWidgets.QFrame.Box)
        self.bottomLayout = QtWidgets.QGridLayout(self.bottomContainer)
        
        self.thdLabel = QtWidgets.QLabel(self.bottomContainer)
        self.thdLabel.setText("当前门限偏移")
        self.thdLabel.setGeometry(QtCore.QRect(200,50,150,30))
        self.thdValue = QtWidgets.QTextEdit(self.bottomContainer)
        self.thdValue.setGeometry(QtCore.QRect(450,50,200,30))
        self.thdValue.setText('5')
        
        self.thdApplyBtn = QtWidgets.QPushButton(self.bottomContainer)
        self.thdApplyBtn.setGeometry(QtCore.QRect(350,100,150,30))
        self.thdApplyBtn.setText('应用')

        
        self.horizontalLayout.addWidget(self.topContainer,0,0,1,1)
        self.horizontalLayout.addWidget(self.bottomContainer,1,0,1,1)
        self.autoMode.setChecked(True)
        
        
        BlackBirdPanel_MainWindow.setCentralWidget(self.centralwidget)
    
    

class adjustThd_ejectWindow(QtWidgets.QMainWindow, ejectWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        
